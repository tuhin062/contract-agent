"""
Enhanced RAG service with advanced retrieval, reranking, and hallucination prevention.
Designed for maximum legal accuracy and grounding.
"""
from typing import List, Dict, Optional, Any, Tuple
import logging
import re
import time
from collections import defaultdict

from app.services.pinecone_client import pinecone_client
from app.services.openrouter import openrouter_client
from app.services.embedding import embedding_service
from app.services.query_rewriter import query_rewriter

logger = logging.getLogger(__name__)


class EnhancedRAGService:
    """
    Advanced RAG service for legal document analysis.
    Features:
    - Hybrid retrieval (semantic + keyword)
    - Advanced reranking
    - Section-aware context building
    - Post-answer verification
    - Hallucination prevention
    """
    
    # Legal intent keywords for query enhancement
    LEGAL_INTENT_KEYWORDS = {
        "payment": ["payment", "compensation", "fee", "invoice", "billing", "price", "cost", "amount"],
        "termination": ["termination", "terminate", "cancel", "expire", "end", "termination clause"],
        "liability": ["liability", "liable", "damage", "loss", "responsible"],
        "indemnification": ["indemnif", "indemnity", "hold harmless", "defend"],
        "scope": ["scope", "work", "services", "deliverables", "obligations"],
        "confidentiality": ["confidential", "non-disclosure", "nda", "proprietary", "secret"],
        "warranty": ["warranty", "warrant", "guarantee", "representation"],
        "insurance": ["insurance", "coverage", "policy", "insured"],
        "dispute": ["dispute", "arbitration", "mediation", "jurisdiction", "governing law"],
    }
    
    def __init__(self):
        """Initialize enhanced RAG service."""
        self.pinecone = pinecone_client
        self.llm = openrouter_client
        self.embedder = embedding_service
    
    async def retrieve_context_enhanced(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        top_k: int = 12,  # Retrieve more for reranking
        min_score: float = 0.20,  # Lower threshold for better retrieval
        use_hybrid: bool = True,
        enforce_diversity: bool = True
    ) -> List[Dict]:
        """
        Enhanced retrieval with hybrid search and diversity enforcement.
        
        Args:
            query: User's question
            file_ids: Optional list of file IDs to filter by
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score threshold
            use_hybrid: Use keyword boosting in addition to semantic search
            enforce_diversity: Ensure chunks come from different sections
            
        Returns:
            List of relevant chunks with enhanced metadata
        """
        logger.info(f"Enhanced retrieval for query: '{query[:100]}...'")
        
        # Step 0: Rewrite query for better retrieval (non-blocking)
        rewritten_query = query
        try:
            query_info = query_rewriter.rewrite_query(query)
            rewritten_query = query_info.get("rewritten", query)
            intent = query_info.get("intent")
            logger.info(f"Query rewritten: '{query}' -> '{rewritten_query}' (intent: {intent})")
        except Exception as e:
            logger.warning(f"Query rewriting failed: {str(e)}, using original query")
            rewritten_query = query
        
        # Step 1: Generate query embedding (use rewritten query)
        query_embedding = await self.embedder.generate_embedding(rewritten_query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        # Normalize embedding dimension
        if len(query_embedding) != 1536:
            if len(query_embedding) > 1536:
                query_embedding = query_embedding[:1536]
            else:
                query_embedding = query_embedding + [0.0] * (1536 - len(query_embedding))
        
        # Step 2: Build filter
        filter_dict = None
        if file_ids:
            file_id_strings = [str(fid) for fid in file_ids]
            if len(file_id_strings) == 1:
                filter_dict = {"file_id": file_id_strings[0]}
            else:
                filter_dict = {"file_id": {"$in": file_id_strings}}
        
        # Step 3: Retrieve more candidates for reranking
        initial_k = top_k * 3 if enforce_diversity else top_k * 2
        results = self.pinecone.query_vectors(
            query_vector=query_embedding,
            top_k=initial_k,
            filter_dict=filter_dict
        )
        
        logger.info(f"Retrieved {len(results)} candidates from Pinecone")
        
        # Log if no results found - try without filter if filter was applied
        if not results:
            logger.warning(f"No results retrieved from Pinecone for query: '{query[:100]}...'")
            logger.warning(f"Filter used: {filter_dict}")
            
            # If filter was applied and no results, try without filter
            if filter_dict:
                logger.info(f"Retrying query without file_id filter...")
                results = self.pinecone.query_vectors(
                    query_vector=query_embedding,
                    top_k=initial_k,
                    filter_dict=None  # Remove filter
                )
                logger.info(f"Retry without filter returned {len(results)} results")
            
            # If still no results, check index status
            if not results:
                try:
                    stats = self.pinecone.get_index_stats()
                    total_vectors = stats.get("total_vector_count", 0)
                    logger.warning(f"Pinecone index has {total_vectors} total vectors")
                    if total_vectors == 0:
                        logger.error("Pinecone index is empty! Documents may not be indexed.")
                except Exception as e:
                    logger.error(f"Could not get index stats: {e}")
                return []
        
        # Step 4: Apply keyword boosting if hybrid search enabled
        if use_hybrid:
            results = self._apply_keyword_boosting(query, results)
        
        # Step 5: Filter by minimum score (with adaptive fallback)
        relevant_chunks = []
        all_scores = []
        for result in results:
            score = result.get("score", 0)
            all_scores.append(score)
            if score >= min_score:
                chunk = {
                    "text": result["metadata"].get("text", ""),
                    "score": score,
                    "file_id": result["metadata"].get("file_id"),
                    "filename": result["metadata"].get("filename"),
                    "page": result["metadata"].get("page"),
                    "chunk_index": result["metadata"].get("chunk_index"),
                    "section_title": result["metadata"].get("section_title"),
                    "detected_clauses": result["metadata"].get("detected_clauses", [])
                }
                relevant_chunks.append(chunk)
        
        # Log score distribution for debugging
        if all_scores:
            logger.info(f"Score distribution - Min: {min(all_scores):.3f}, Max: {max(all_scores):.3f}, Avg: {sum(all_scores)/len(all_scores):.3f}, Threshold: {min_score}")
            logger.info(f"Top 5 raw scores: {sorted(all_scores, reverse=True)[:5]}")
        
        # Adaptive fallback: If no chunks meet threshold but we have results, use top results anyway
        if not relevant_chunks and results:
            logger.warning(f"No chunks met min_score threshold ({min_score}), but {len(results)} results found. Using top results with lower threshold.")
            # Use a very lenient threshold - take top results regardless of score
            adaptive_threshold = 0.1  # Very low threshold to ensure we get results
            for result in results:
                score = result.get("score", 0)
                if score >= adaptive_threshold:
                    chunk = {
                        "text": result["metadata"].get("text", ""),
                        "score": score,
                        "file_id": result["metadata"].get("file_id"),
                        "filename": result["metadata"].get("filename"),
                        "page": result["metadata"].get("page"),
                        "chunk_index": result["metadata"].get("chunk_index"),
                        "section_title": result["metadata"].get("section_title"),
                        "detected_clauses": result["metadata"].get("detected_clauses", [])
                    }
                    relevant_chunks.append(chunk)
                    if len(relevant_chunks) >= top_k:  # Limit to top_k even with fallback
                        break
            
            # If still no chunks, take top results regardless of score
            if not relevant_chunks:
                logger.warning(f"Taking top {min(top_k, len(results))} results regardless of score")
                for i, result in enumerate(results[:top_k]):
                    chunk = {
                        "text": result["metadata"].get("text", ""),
                        "score": result.get("score", 0),
                        "file_id": result["metadata"].get("file_id"),
                        "filename": result["metadata"].get("filename"),
                        "page": result["metadata"].get("page"),
                        "chunk_index": result["metadata"].get("chunk_index"),
                        "section_title": result["metadata"].get("section_title"),
                        "detected_clauses": result["metadata"].get("detected_clauses", [])
                    }
                    relevant_chunks.append(chunk)
            
            logger.info(f"Fallback retrieval: {len(relevant_chunks)} chunks using adaptive threshold {adaptive_threshold}")
        
        # Step 6: Enforce diversity (avoid too many chunks from same section)
        if enforce_diversity and relevant_chunks:
            relevant_chunks = self._enforce_diversity(relevant_chunks, top_k)
        
        # Step 7: Advanced reranking (non-blocking - preserve chunks if reranking fails)
        if relevant_chunks:
            try:
                reranked = self._advanced_rerank(query, relevant_chunks)
                if reranked and len(reranked) > 0:
                    relevant_chunks = reranked[:top_k]
                else:
                    logger.warning("Reranking returned empty results, using original chunks")
                    relevant_chunks = relevant_chunks[:top_k]
            except Exception as e:
                logger.warning(f"Reranking failed: {str(e)}, using original chunks")
                relevant_chunks = relevant_chunks[:top_k]
        
        logger.info(f"Final retrieval: {len(relevant_chunks)} chunks after reranking")
        
        # Log top scores
        if relevant_chunks:
            top_scores = [c.get("reranked_score", c["score"]) for c in relevant_chunks[:5]]
            logger.info(f"Top 5 reranked scores: {top_scores}")
        
        return relevant_chunks
    
    def _apply_keyword_boosting(self, query: str, results: List[Dict]) -> List[Dict]:
        """Boost results that contain query keywords."""
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))
        
        # Detect legal intent
        detected_intent = None
        for intent, keywords in self.LEGAL_INTENT_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intent = intent
                break
        
        for result in results:
            text_lower = result["metadata"].get("text", "").lower()
            base_score = result.get("score", 0)
            
            # Boost for exact keyword matches
            keyword_matches = sum(1 for term in query_terms if term in text_lower)
            keyword_boost = keyword_matches * 0.03
            
            # Boost for legal intent match
            intent_boost = 0.0
            if detected_intent:
                detected_clauses = result["metadata"].get("detected_clauses", [])
                if detected_intent in detected_clauses:
                    intent_boost = 0.05
            
            # Boost for section title relevance
            section_title = result["metadata"].get("section_title", "").lower()
            section_boost = 0.0
            if section_title:
                if any(term in section_title for term in query_terms):
                    section_boost = 0.04
            
            # Apply boosts
            result["score"] = min(1.0, base_score + keyword_boost + intent_boost + section_boost)
            result["boosts"] = {
                "keyword": keyword_boost,
                "intent": intent_boost,
                "section": section_boost
            }
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _enforce_diversity(self, chunks: List[Dict], max_chunks: int) -> List[Dict]:
        """Ensure chunks come from different sections/files."""
        selected = []
        seen_sections = set()
        seen_files = defaultdict(int)
        max_per_file = max(1, max_chunks // 2)  # At most half from one file
        
        for chunk in chunks:
            file_id = chunk.get("file_id")
            section_title = chunk.get("section_title", "")
            section_key = f"{file_id}:{section_title}"
            
            # Check if we've seen this section too many times
            if section_key in seen_sections and len(selected) >= max_chunks:
                continue
            
            # Check if we've seen this file too many times
            if file_id and seen_files[file_id] >= max_per_file:
                continue
            
            selected.append(chunk)
            seen_sections.add(section_key)
            if file_id:
                seen_files[file_id] += 1
            
            if len(selected) >= max_chunks:
                break
        
        return selected
    
    def _advanced_rerank(self, query: str, chunks: List[Dict]) -> List[Dict]:
        """Advanced reranking using multiple signals."""
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))
        
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            base_score = chunk.get("score", 0)
            
            # Signal 1: Exact term matches
            term_matches = sum(1 for term in query_terms if term in text_lower)
            term_score = term_matches / max(len(query_terms), 1) * 0.2
            
            # Signal 2: Legal phrase matches
            legal_phrases = [
                "payment terms", "termination clause", "scope of work",
                "liability", "indemnification", "confidentiality"
            ]
            phrase_matches = sum(1 for phrase in legal_phrases if phrase in query_lower and phrase in text_lower)
            phrase_score = phrase_matches * 0.1
            
            # Signal 3: Section title relevance
            section_title = chunk.get("section_title", "").lower()
            section_score = 0.0
            if section_title:
                section_words = set(re.findall(r'\b\w+\b', section_title))
                section_overlap = len(query_terms & section_words) / max(len(query_terms), 1)
                section_score = section_overlap * 0.15
            
            # Signal 4: Position in document (prefer earlier sections for general queries)
            position_score = 0.0
            chunk_index = chunk.get("chunk_index", 0)
            if chunk_index < 10:  # First 10 chunks
                position_score = 0.05
            
            # Combine signals
            reranked_score = base_score + term_score + phrase_score + section_score + position_score
            chunk["reranked_score"] = min(1.0, reranked_score)
        
        return sorted(chunks, key=lambda x: x.get("reranked_score", x["score"]), reverse=True)
    
    def build_enhanced_context(self, chunks: List[Dict]) -> Tuple[str, Dict]:
        """
        Build enhanced context with section organization and citations.
        
        Returns:
            Tuple of (context_text, context_metadata)
        """
        if not chunks:
            return "", {}
        
        # Organize chunks by section
        sections = defaultdict(list)
        for i, chunk in enumerate(chunks):
            section_title = chunk.get("section_title", "General")
            if not section_title:
                section_title = "General"
            sections[section_title].append((i, chunk))
        
        # Build context with proper citations
        context_parts = []
        source_map = {}  # Map source numbers to chunk info
        
        source_num = 1
        for section_title, section_chunks in sections.items():
            if section_title != "General":
                context_parts.append(f"\n=== {section_title} ===\n")
            
            for chunk_idx, chunk in section_chunks:
                filename = chunk.get("filename", "Document")
                page = chunk.get("page")
                text = chunk["text"]
                
                # Create citation
                citation = f"[Source {source_num}]"
                if page:
                    citation += f" {filename}, Page {page}"
                else:
                    citation += f" {filename}"
                
                source_map[source_num] = {
                    "filename": filename,
                    "page": page,
                    "section_title": section_title,
                    "chunk_index": chunk.get("chunk_index")
                }
                
                context_parts.append(f"{citation}\n{text}\n")
                source_num += 1
        
        context_text = "\n".join(context_parts)
        
        # Detect missing exhibits
        missing_exhibits = self._detect_missing_exhibits(context_text)
        
        context_metadata = {
            "total_chunks": len(chunks),
            "sections": list(sections.keys()),
            "source_map": source_map,
            "missing_exhibits": missing_exhibits
        }
        
        return context_text, context_metadata
    
    def _detect_missing_exhibits(self, text: str) -> List[str]:
        """Detect references to exhibits that might be missing."""
        exhibit_patterns = [
            r'Exhibit\s+([A-Z])',
            r'Attachment\s+([A-Z])',
            r'Appendix\s+([A-Z])',
            r'Schedule\s+([A-Z])'
        ]
        
        referenced_exhibits = set()
        for pattern in exhibit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            referenced_exhibits.update(matches)
        
        # Check if exhibit content is present
        missing = []
        for exhibit in referenced_exhibits:
            # Look for exhibit content (heuristic: if exhibit is mentioned but no substantial content follows)
            exhibit_mention = re.search(
                rf'Exhibit\s+{exhibit}[^.]{{0,200}}',
                text,
                re.IGNORECASE
            )
            if exhibit_mention:
                # Check if there's substantial content after mention
                mention_end = exhibit_mention.end()
                following_text = text[mention_end:mention_end+500]
                if len(following_text.strip()) < 100:  # Likely missing
                    missing.append(f"Exhibit {exhibit}")
        
        return missing
    
    async def generate_grounded_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate answer with strict grounding enforcement.
        
        Args:
            query: User's question
            context_chunks: Retrieved context chunks
            chat_history: Previous messages
            
        Returns:
            Complete response with verification
        """
        start_time = time.time()
        
        # Build enhanced context
        context_text, context_metadata = self.build_enhanced_context(context_chunks)
        
        # Create strict system prompt
        system_prompt = self._create_strict_prompt(context_text, context_metadata)
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            messages.extend(chat_history[-6:])
        
        messages.append({"role": "user", "content": query})
        
        # Generate initial answer
        try:
            response = await self.llm.chat_completion(
                messages=messages,
                model_type="chat",
                temperature=0.0,  # Zero temperature for maximum accuracy
                max_tokens=2000
            )
            
            draft_answer = response["choices"][0]["message"]["content"]
            model_used = response.get("model_used", "unknown")
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            
            # Post-answer verification
            verified_answer = await self._verify_answer(draft_answer, context_chunks, query)
            
            # Calculate confidence
            avg_score = sum(c.get("reranked_score", c["score"]) for c in context_chunks) / len(context_chunks) if context_chunks else 0
            confidence = "high" if avg_score >= 0.75 else "medium" if avg_score >= 0.55 else "low"
            
            result = {
                "answer": verified_answer["answer"],
                "sources": self._extract_sources(context_chunks),
                "confidence": confidence,
                "model_used": model_used,
                "tokens_used": tokens_used,
                "retrieved_chunks": len(context_chunks),
                "response_time_ms": int((time.time() - start_time) * 1000),
                "verification": verified_answer.get("verification", {}),
                "missing_exhibits": context_metadata.get("missing_exhibits", [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}", exc_info=True)
            return {
                "answer": "I encountered an error while processing your request. Please try again.",
                "sources": [],
                "confidence": "error",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _create_strict_prompt(self, context_text: str, context_metadata: Dict) -> str:
        """Create extremely strict prompt to prevent hallucination."""
        missing_exhibits = context_metadata.get("missing_exhibits", [])
        missing_warning = ""
        if missing_exhibits:
            missing_warning = f"\n\n⚠️ IMPORTANT: The following exhibits are referenced but may be missing from the provided context: {', '.join(missing_exhibits)}. Do NOT invent their contents."
        
        return f"""You are an expert legal document analyst. Your responses MUST be 100% grounded in the provided context.

CRITICAL RULES - VIOLATION CAUSES HALLUCINATION:

1. ONLY use information EXPLICITLY present in the context below
2. ALWAYS cite sources using [Source X] format for EVERY factual claim
3. If information is NOT in the context, you MUST say: "This information is not present in the provided documents."
4. NEVER invent, assume, or infer information not in the context
5. NEVER make up section numbers, clause numbers, or page references
6. NEVER invent payment terms, termination conditions, or other contract details
7. If asked about something not in context, explicitly state it's not found
8. Quote relevant text using "quotation marks" when helpful
9. Distinguish between what IS stated vs what might be implied (only state what IS stated)

CITATION REQUIREMENTS:
- Every factual statement MUST have [Source X] citation
- If you cannot cite a source, the statement is likely hallucinated - DO NOT INCLUDE IT
- Section/page references must match exactly what's in the context

RESPONSE STRUCTURE:
1. Direct answer to the question (with citations)
2. Supporting evidence from context (quoted when helpful)
3. Any limitations or missing information
4. Caveats about incomplete context

{missing_warning}

CONTEXT DOCUMENTS:
{context_text}

Remember: If it's not in the context, it doesn't exist. State "Not found in provided context" rather than inventing."""
    
    async def _verify_answer(
        self,
        draft_answer: str,
        context_chunks: List[Dict],
        original_query: str
    ) -> Dict:
        """
        Verify that the answer is grounded in context.
        Uses LLM to check each claim against retrieved chunks.
        """
        # Extract all text from context
        context_text = " ".join(c["text"] for c in context_chunks)
        
        verification_prompt = f"""You are a fact-checker. Verify that every factual claim in the answer below is supported by the context.

Answer to verify:
{draft_answer}

Context:
{context_text[:4000]}

For each factual claim in the answer:
1. Check if it appears in the context
2. If not found, mark it as UNGROUNDED
3. If found, confirm it's GROUNDED

Return a JSON object with:
{{
  "grounded_claims": ["claim 1", "claim 2"],
  "ungrounded_claims": ["claim 3"],
  "verification_status": "all_grounded" | "some_ungrounded" | "mostly_ungrounded",
  "revised_answer": "answer with ungrounded claims removed or flagged"
}}

If there are ungrounded claims, provide a revised answer that removes or flags them."""
        
        try:
            response = await self.llm.chat_completion(
                messages=[{"role": "user", "content": verification_prompt}],
                model_type="chat",
                temperature=0.0,
                max_tokens=2000
            )
            
            verification_text = response["choices"][0]["message"]["content"]
            
            # Try to parse JSON
            import json
            if "{" in verification_text and "}" in verification_text:
                json_start = verification_text.find("{")
                json_end = verification_text.rfind("}") + 1
                json_str = verification_text[json_start:json_end]
                verification_data = json.loads(json_str)
                
                return {
                    "answer": verification_data.get("revised_answer", draft_answer),
                    "verification": verification_data
                }
            else:
                # Fallback: return original answer
                return {"answer": draft_answer, "verification": {"status": "manual_review_needed"}}
                
        except Exception as e:
            logger.warning(f"Verification failed: {str(e)}, using original answer")
            return {"answer": draft_answer, "verification": {"status": "verification_failed"}}
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Extract source information from chunks."""
        sources = []
        seen = set()
        
        for i, chunk in enumerate(chunks, 1):
            source_key = (chunk.get("file_id"), chunk.get("page"), chunk.get("chunk_index"))
            if source_key in seen:
                continue
            seen.add(source_key)
            
            sources.append({
                "text": chunk["text"][:300],
                "score": chunk.get("reranked_score", chunk.get("score", 0)),
                "file_id": chunk.get("file_id"),
                "filename": chunk.get("filename"),
                "page": chunk.get("page"),
                "chunk_index": chunk.get("chunk_index"),
                "section_title": chunk.get("section_title")
            })
        
        return sources
    
    async def chat(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict]] = None,
        top_k: int = 10,
        stream: bool = False,
        include_follow_ups: bool = True,
        include_clause_analysis: bool = True
    ) -> Dict:
        """
        Complete enhanced RAG chat flow.
        
        Args:
            query: User's question
            file_ids: Optional file IDs for context
            chat_history: Previous messages
            top_k: Number of context chunks to retrieve
            stream: Whether to stream response
            include_follow_ups: Include follow-up suggestions
            include_clause_analysis: Include clause/risk analysis
            
        Returns:
            Complete response dict
        """
        # Step 1: Enhanced retrieval (use lower min_score for better retrieval)
        context_chunks = await self.retrieve_context_enhanced(
            query=query,
            file_ids=file_ids,
            top_k=top_k,
            min_score=0.15,  # Very low threshold - adaptive fallback will handle quality
            use_hybrid=True,
            enforce_diversity=True
        )
        
        # Handle no context
        if not context_chunks:
            return {
                "answer": "I don't have any relevant information in the uploaded documents to answer your question. Please ensure you've uploaded relevant documents, or try rephrasing your question.",
                "sources": [],
                "confidence": "low",
                "retrieved_chunks": 0,
                "follow_up_suggestions": [
                    "What documents do you have access to?",
                    "Can you help me upload a document?",
                    "What types of questions can you answer?"
                ]
            }
        
        # Step 2: Generate grounded answer
        result = await self.generate_grounded_answer(
            query=query,
            context_chunks=context_chunks,
            chat_history=chat_history
        )
        
        result["retrieved_chunks"] = len(context_chunks)
        return result


# Global enhanced RAG service instance
enhanced_rag_service = EnhancedRAGService()

