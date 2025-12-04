"""
Enhanced RAG (Retrieval-Augmented Generation) service.
Combines vector search with LLM generation for context-aware, legally accurate responses.
Features: Streaming, follow-up suggestions, clause extraction, risk highlighting.
"""
from typing import List, Dict, Optional, Any, AsyncGenerator
import logging
import json
import re
import time
from app.services.pinecone_client import pinecone_client
from app.services.openrouter import openrouter_client
from app.services.embedding import embedding_service

logger = logging.getLogger(__name__)


class EnhancedRAGService:
    """Service for RAG-powered question answering with legal focus."""
    
    # Legal clause patterns for extraction
    CLAUSE_PATTERNS = {
        "payment": r"payment|compensation|fee|price|cost|invoice|billing",
        "termination": r"termination|terminate|cancel|end of agreement|expir",
        "liability": r"liability|liable|indemnif|damage|loss",
        "confidentiality": r"confidential|non-disclosure|nda|proprietary|secret",
        "ip_rights": r"intellectual property|patent|copyright|trademark|license",
        "dispute_resolution": r"dispute|arbitration|mediation|jurisdiction|governing law",
        "warranty": r"warranty|warrant|guarantee|representation",
        "force_majeure": r"force majeure|act of god|unforeseen|beyond control",
        "indemnification": r"indemnif|hold harmless|defend",
        "limitation": r"limitation|limit|cap|maximum|ceiling"
    }
    
    # Risk indicators
    RISK_PATTERNS = {
        "high": [
            r"unlimited liability",
            r"sole discretion",
            r"waive.{0,20}right",
            r"perpetual.{0,20}license",
            r"automatic renewal",
            r"unilateral.{0,20}change",
            r"non-negotiable"
        ],
        "medium": [
            r"reasonable.{0,20}efforts?",
            r"best efforts?",
            r"material breach",
            r"cure period",
            r"notice.{0,20}days"
        ]
    }
    
    def __init__(self):
        """Initialize enhanced RAG service."""
        self.pinecone = pinecone_client
        self.llm = openrouter_client
        self.embedder = embedding_service
    
    async def retrieve_context(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        top_k: int = 10,
        min_score: float = 0.4,  # Lowered from 0.65 to 0.4 for better retrieval
        rerank: bool = True
    ) -> List[Dict]:
        """
        Retrieve relevant context chunks with reranking.
        
        Args:
            query: User's question
            file_ids: Optional list of file IDs to filter by
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score threshold (lowered to 0.4 for better retrieval)
            rerank: Whether to rerank results for relevance
            
        Returns:
            List of relevant chunks with metadata
        """
        logger.info(f"Retrieving context for query: '{query[:100]}...' (file_ids={file_ids}, top_k={top_k}, min_score={min_score})")
        
        # Generate embedding for query
        query_embedding = await self.embedder.generate_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []
        
        logger.info(f"Query embedding generated: dimension={len(query_embedding)}")
        
        # Verify embedding dimension (should be 1536 for text-embedding-3-small)
        if len(query_embedding) != 1536:
            logger.warning(f"Query embedding has unexpected dimension: {len(query_embedding)} (expected 1536)")
            if len(query_embedding) > 1536:
                query_embedding = query_embedding[:1536]
                logger.warning("Truncated query embedding to 1536 dimensions")
            elif len(query_embedding) < 1536:
                # Pad with zeros
                query_embedding = query_embedding + [0.0] * (1536 - len(query_embedding))
                logger.warning("Padded query embedding to 1536 dimensions")
        
        # Build filter for specific files
        # Pinecone filter syntax: for multiple values, use $in operator
        filter_dict = None
        if file_ids:
            # Convert file_ids to strings and create filter
            file_id_strings = [str(fid) for fid in file_ids]
            if len(file_id_strings) == 1:
                # Single file ID - use simple equality
                filter_dict = {"file_id": file_id_strings[0]}
            else:
                # Multiple file IDs - use $in operator
                filter_dict = {"file_id": {"$in": file_id_strings}}
            logger.info(f"Filtering by file_ids: {file_ids}")
        else:
            logger.info("No file_ids provided - searching all documents")
        
        # Query Pinecone with higher top_k for reranking
        initial_k = top_k * 2 if rerank else top_k
        logger.info(f"Querying Pinecone with top_k={initial_k}, filter={filter_dict}")
        
        results = self.pinecone.query_vectors(
            query_vector=query_embedding,
            top_k=initial_k,
            filter_dict=filter_dict
        )
        
        logger.info(f"Pinecone returned {len(results)} results (before filtering by min_score)")
        
        # If no results, try without filter (in case filter syntax is wrong)
        if not results and filter_dict:
            logger.warning("No results with filter, trying without filter...")
            results = self.pinecone.query_vectors(
                query_vector=query_embedding,
                top_k=initial_k,
                filter_dict=None
            )
            logger.info(f"Query without filter returned {len(results)} results")
        
        # Filter by minimum score (lowered threshold for better retrieval)
        relevant_chunks = []
        for result in results:
            score = result["score"]
            if score >= min_score:
                chunk = {
                    "text": result["metadata"].get("text", ""),
                    "score": score,
                    "file_id": result["metadata"].get("file_id"),
                    "filename": result["metadata"].get("filename"),
                    "page": result["metadata"].get("page"),
                    "chunk_index": result["metadata"].get("chunk_index")
                }
                relevant_chunks.append(chunk)
            else:
                logger.debug(f"Chunk filtered out: score={score:.3f} < min_score={min_score}")
        
        logger.info(f"After filtering: {len(relevant_chunks)} chunks with score >= {min_score}")
        
        # If still no results, try with even lower threshold (0.3) for general queries
        if not relevant_chunks and results:
            logger.warning(f"No chunks passed min_score={min_score}, trying with lower threshold (0.3)...")
            fallback_min_score = 0.3
            for result in results:
                score = result["score"]
                if score >= fallback_min_score:
                    chunk = {
                        "text": result["metadata"].get("text", ""),
                        "score": score,
                        "file_id": result["metadata"].get("file_id"),
                        "filename": result["metadata"].get("filename"),
                        "page": result["metadata"].get("page"),
                        "chunk_index": result["metadata"].get("chunk_index")
                    }
                    relevant_chunks.append(chunk)
            logger.info(f"Fallback threshold returned {len(relevant_chunks)} chunks")
        
        # Rerank by extracting key terms and boosting relevant chunks
        if rerank and relevant_chunks:
            relevant_chunks = self._rerank_chunks(query, relevant_chunks)[:top_k]
            logger.info(f"After reranking: {len(relevant_chunks)} chunks")
        
        # Log top scores for debugging
        if relevant_chunks:
            top_scores = [c["score"] for c in relevant_chunks[:5]]
            logger.info(f"Top 5 scores: {top_scores}")
        else:
            if results:
                top_scores = [r["score"] for r in results[:5]]
                logger.warning(f"No chunks passed min_score filter. Top 5 raw scores: {top_scores}")
            else:
                logger.warning("No results returned from Pinecone at all")
        
        return relevant_chunks
    
    def _rerank_chunks(self, query: str, chunks: List[Dict]) -> List[Dict]:
        """Simple keyword-based reranking."""
        query_terms = set(query.lower().split())
        
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            
            # Boost score based on exact term matches
            match_count = sum(1 for term in query_terms if term in text_lower)
            boost = match_count * 0.05
            
            # Additional boost for legal terms if query contains them
            legal_terms = ["clause", "section", "article", "paragraph", "provision", "term"]
            if any(term in query.lower() for term in legal_terms):
                if any(term in text_lower for term in legal_terms):
                    boost += 0.1
            
            chunk["reranked_score"] = min(1.0, chunk["score"] + boost)
        
        return sorted(chunks, key=lambda x: x.get("reranked_score", x["score"]), reverse=True)
    
    def _extract_clauses(self, text: str) -> List[Dict]:
        """Extract legal clauses from text."""
        clauses = []
        text_lower = text.lower()
        
        for clause_type, pattern in self.CLAUSE_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Find the sentence containing the clause
                sentences = text.split(".")
                for sentence in sentences:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        clauses.append({
                            "type": clause_type,
                            "text": sentence.strip()[:200],
                            "confidence": "high" if len(re.findall(pattern, sentence, re.IGNORECASE)) > 1 else "medium"
                        })
                        break
        
        return clauses
    
    def _highlight_risks(self, text: str) -> List[Dict]:
        """Identify potential risks in text."""
        risks = []
        text_lower = text.lower()
        
        for severity, patterns in self.RISK_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Get surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    risks.append({
                        "severity": severity,
                        "matched_text": match.group(),
                        "context": f"...{context}...",
                        "recommendation": self._get_risk_recommendation(pattern)
                    })
        
        return risks
    
    def _get_risk_recommendation(self, pattern: str) -> str:
        """Get recommendation for a risk pattern."""
        recommendations = {
            "unlimited liability": "Negotiate a liability cap",
            "sole discretion": "Request mutual consent requirements",
            "waive": "Review waived rights carefully",
            "perpetual": "Consider term limits",
            "automatic renewal": "Add opt-out provisions",
            "unilateral": "Request bilateral amendment rights",
            "non-negotiable": "Flag for legal review"
        }
        
        for key, rec in recommendations.items():
            if key in pattern:
                return rec
        return "Review with legal counsel"
    
    async def generate_follow_up_suggestions(
        self,
        query: str,
        answer: str,
        context_summary: str
    ) -> List[str]:
        """Generate smart follow-up question suggestions."""
        prompt = f"""Based on this Q&A about a legal document, suggest exactly 3 relevant follow-up questions the user might want to ask.

Original Question: {query}

Answer Given: {answer[:500]}

Document Context: {context_summary[:300]}

Return ONLY a JSON array of 3 question strings, no other text:
["question 1", "question 2", "question 3"]"""
        
        try:
            response = await self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model_type="chat",
                temperature=0.3,
                max_tokens=200
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # Parse JSON array
            if "[" in content and "]" in content:
                json_str = content[content.index("["):content.rindex("]")+1]
                suggestions = json.loads(json_str)
                return suggestions[:3]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate follow-ups: {str(e)}")
            return []
    
    async def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        chat_history: Optional[List[Dict]] = None,
        include_follow_ups: bool = True,
        include_clause_analysis: bool = True
    ) -> Dict:
        """
        Generate answer using retrieved context with enhanced features.
        
        Args:
            query: User's question
            context_chunks: Retrieved context chunks
            chat_history: Previous messages
            include_follow_ups: Generate follow-up suggestions
            include_clause_analysis: Extract clauses and risks
            
        Returns:
            Complete response with answer, sources, and metadata
        """
        start_time = time.time()
        
        # Build context string from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks):
            source_info = f"[Source {i+1}]"
            if chunk.get("filename"):
                source_info += f" {chunk['filename']}"
            if chunk.get("page"):
                source_info += f" (Page {chunk['page']})"
            context_parts.append(f"{source_info}\n{chunk['text']}")
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        # Enhanced system prompt for legal accuracy
        system_prompt = """You are an expert legal document analyst. Your responses must be:

CRITICAL RULES - FOLLOW EXACTLY:
1. ONLY use information explicitly present in the provided context documents
2. ALWAYS cite sources using [Source X] format for every factual claim
3. If information is NOT in the context, say: "This information is not present in the provided documents."
4. NEVER assume, infer, or make up information
5. Quote relevant text when helpful (use "quotation marks")
6. If confidence is low, explicitly state: "Note: This interpretation has limited context support."
7. Use precise legal language appropriate for the document type

RESPONSE FORMAT:
- Start with a direct answer to the question
- Support with specific citations [Source X]
- Highlight any ambiguities or areas needing clarification
- End with any relevant caveats

Context Documents:
{context}"""

        messages = [
            {
                "role": "system",
                "content": system_prompt.format(context=context_text)
            }
        ]
        
        # Add chat history
        if chat_history:
            messages.extend(chat_history[-6:])  # Last 6 messages for context
        
        messages.append({
            "role": "user",
            "content": query
        })
        
        try:
            response = await self.llm.chat_completion(
                messages=messages,
                model_type="chat",
                temperature=0.1,  # Very low for factual accuracy
                max_tokens=1500
            )
            
            answer = response["choices"][0]["message"]["content"]
            model_used = response.get("model_used", "unknown")
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            
            # Calculate confidence
            avg_score = sum(c["score"] for c in context_chunks) / len(context_chunks) if context_chunks else 0
            confidence = "high" if avg_score >= 0.85 else "medium" if avg_score >= 0.70 else "low"
            
            result = {
                "answer": answer,
                "sources": context_chunks,
                "confidence": confidence,
                "model_used": model_used,
                "tokens_used": tokens_used,
                "retrieved_chunks": len(context_chunks),
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
            
            # Extract clauses and risks from context
            if include_clause_analysis:
                all_text = " ".join(c["text"] for c in context_chunks)
                result["extracted_clauses"] = self._extract_clauses(all_text)
                result["risk_highlights"] = self._highlight_risks(all_text)
            
            # Generate follow-up suggestions
            if include_follow_ups:
                context_summary = all_text[:500] if context_chunks else ""
                result["follow_up_suggestions"] = await self.generate_follow_up_suggestions(
                    query, answer, context_summary
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": "I encountered an error while processing your request. Please try again.",
                "sources": [],
                "confidence": "error",
                "error": str(e),
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def generate_answer_stream(
        self,
        query: str,
        context_chunks: List[Dict],
        chat_history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream answer generation for real-time responses.
        
        Args:
            query: User's question
            context_chunks: Retrieved context chunks
            chat_history: Previous messages
            
        Yields:
            Streamed text chunks
        """
        # Build context
        context_parts = []
        for i, chunk in enumerate(context_chunks):
            source_info = f"[Source {i+1}]"
            if chunk.get("filename"):
                source_info += f" {chunk['filename']}"
            if chunk.get("page"):
                source_info += f" (Page {chunk['page']})"
            context_parts.append(f"{source_info}\n{chunk['text']}")
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        system_prompt = """You are an expert legal document analyst. Your responses must be:

CRITICAL RULES:
1. ONLY use information explicitly present in the context documents
2. ALWAYS cite sources using [Source X] format for every claim
3. If information is NOT in the context, say: "This information is not present in the provided documents."
4. NEVER assume or make up information
5. Quote relevant text when helpful

Context Documents:
{context}"""

        messages = [
            {"role": "system", "content": system_prompt.format(context=context_text)}
        ]
        
        if chat_history:
            messages.extend(chat_history[-6:])
        
        messages.append({"role": "user", "content": query})
        
        async for chunk in self.llm.chat_completion_stream(
            messages=messages,
            model_type="chat",
            temperature=0.1
        ):
            yield chunk
    
    async def chat(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict]] = None,
        top_k: int = 8,
        stream: bool = False,
        include_follow_ups: bool = True,
        include_clause_analysis: bool = True
    ) -> Dict:
        """
        Complete RAG chat flow: retrieve context + generate answer.
        
        Args:
            query: User's question
            file_ids: Optional file IDs for context
            chat_history: Previous messages
            top_k: Number of context chunks to retrieve
            stream: Whether to stream response (returns generator)
            include_follow_ups: Include follow-up suggestions
            include_clause_analysis: Include clause/risk analysis
            
        Returns:
            Complete response dict or generator for streaming
        """
        # Step 1: Retrieve relevant context
        # Use lower min_score for better retrieval, especially for general queries
        context_chunks = await self.retrieve_context(
            query=query,
            file_ids=file_ids,
            top_k=top_k,
            min_score=0.4,  # Lower threshold for better retrieval
            rerank=True
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
        
        # Step 2: Generate answer (streaming or regular)
        if stream:
            return self.generate_answer_stream(
                query=query,
                context_chunks=context_chunks,
                chat_history=chat_history
            )
        
        result = await self.generate_answer(
            query=query,
            context_chunks=context_chunks,
            chat_history=chat_history,
            include_follow_ups=include_follow_ups,
            include_clause_analysis=include_clause_analysis
        )
        
        result["retrieved_chunks"] = len(context_chunks)
        return result


# Global RAG service instance
rag_service = EnhancedRAGService()
