"""
OpenRouter LLM client for chat completions and embeddings.
Provides interface to multiple LLM models through OpenRouter API.
Optimized for legal industry with fallback models and streaming support.
"""
from typing import List, Dict, Optional, AsyncGenerator, Any
import httpx
import json
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API with fallback support and streaming."""
    
    # Model configurations optimized for legal work
    MODEL_CONFIGS = {
        "chat": {
            "primary": settings.OPENROUTER_CHAT_MODEL,
            "fallback": settings.OPENROUTER_CHAT_MODEL_FALLBACK,
            "temperature": settings.LLM_TEMPERATURE_CHAT,
            "max_retries": 2
        },
        "reasoning": {
            "primary": settings.OPENROUTER_REASONING_MODEL,
            "fallback": settings.OPENROUTER_REASONING_MODEL_FALLBACK,
            "temperature": settings.LLM_TEMPERATURE_REASONING,
            "max_retries": 2
        },
        "generation": {
            "primary": settings.OPENROUTER_GENERATION_MODEL,
            "fallback": settings.OPENROUTER_CHAT_MODEL,
            "temperature": settings.LLM_TEMPERATURE_GENERATION,
            "max_retries": 2
        }
    }
    
    def __init__(self):
        """Initialize OpenRouter client."""
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Contract Agent - Legal Document AI"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        model_type: str = "chat"
    ) -> Dict:
        """
        Get chat completion from OpenRouter with automatic fallback.
        
        Args:
            messages: List of message dictionaries with role and content
            model: Model to use (if None, uses config based on model_type)
            temperature: Sampling temperature (if None, uses config)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            model_type: Type of model to use ('chat', 'reasoning', 'generation')
            
        Returns:
            Completion response dictionary
        """
        config = self.MODEL_CONFIGS.get(model_type, self.MODEL_CONFIGS["chat"])
        model = model or config["primary"]
        temperature = temperature if temperature is not None else config["temperature"]
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,  # Nucleus sampling for better quality
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Add legal-focused system instructions if not already present
        if not any(m.get("role") == "system" for m in messages):
            legal_system = {
                "role": "system",
                "content": (
                    "You are a precise legal document assistant. "
                    "CRITICAL: Only state facts that are explicitly present in the provided context. "
                    "If information is not available, clearly state 'This information is not present in the provided documents.' "
                    "Never make assumptions or inferences beyond what is explicitly stated. "
                    "Always cite sources when making claims."
                )
            }
            payload["messages"] = [legal_system] + messages
        
        # Try primary model first, then fallback
        models_to_try = [model]
        if model == config["primary"] and config.get("fallback"):
            models_to_try.append(config["fallback"])
        
        last_error = None
        for attempt_model in models_to_try:
            payload["model"] = attempt_model
            
            for attempt in range(config.get("max_retries", 2)):
                try:
                    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
                        response = await client.post(
                            f"{self.base_url}/chat/completions",
                            headers=self.headers,
                            json=payload
                        )
                        response.raise_for_status()
                        result = response.json()
                        result["model_used"] = attempt_model
                        return result
                        
                except httpx.HTTPStatusError as e:
                    last_error = e
                    if e.response.status_code == 429:  # Rate limit
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                    elif e.response.status_code >= 500:  # Server error
                        logger.warning(f"Server error {e.response.status_code}, retrying...")
                        await asyncio.sleep(1)
                    else:
                        break  # Don't retry on client errors
                        
                except httpx.TimeoutException as e:
                    last_error = e
                    logger.warning(f"Timeout on attempt {attempt + 1}")
                    
                except Exception as e:
                    last_error = e
                    logger.error(f"Unexpected error: {str(e)}")
                    break
            
            if attempt_model != models_to_try[-1]:
                logger.info(f"Falling back from {attempt_model} to {models_to_try[-1]}")
        
        logger.error(f"All models failed: {str(last_error)}")
        raise last_error or Exception("All model attempts failed")
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model_type: str = "chat"
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion from OpenRouter.
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            model_type: Type of model
            
        Yields:
            Streamed text chunks
        """
        config = self.MODEL_CONFIGS.get(model_type, self.MODEL_CONFIGS["chat"])
        model = model or config["primary"]
        temperature = temperature if temperature is not None else config["temperature"]
        
        # Add legal system prompt if needed
        if not any(m.get("role") == "system" for m in messages):
            legal_system = {
                "role": "system",
                "content": (
                    "You are a precise legal document assistant. "
                    "CRITICAL: Only state facts that are explicitly present in the provided context. "
                    "If information is not available, clearly state 'This information is not present in the provided documents.' "
                    "Never make assumptions or inferences beyond what is explicitly stated. "
                    "Always cite sources when making claims."
                )
            }
            messages = [legal_system] + messages
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
            "top_p": 0.95
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("choices"):
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"\n\n[Error: {str(e)}]"
    
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            model: Embedding model (defaults to settings.OPENROUTER_EMBEDDING_MODEL)
            
        Returns:
            Embedding vector (list of floats)
        """
        model = model or settings.OPENROUTER_EMBEDDING_MODEL
        
        # Clean and truncate text if needed
        text = text.strip()
        if not text:
            logger.warning("Empty text provided for embedding")
            # Return zero vector matching expected dimension (1536 for text-embedding-3-small)
            return [0.0] * 1536
        
        # Truncate to avoid token limits (approx 8000 tokens for embedding models)
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} chars for embedding")
        
        payload = {
            "model": model,
            "input": text
        }
        
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
                    response = await client.post(
                        f"{self.base_url}/embeddings",
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    embedding = result["data"][0]["embedding"]
                    return embedding
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Embedding rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"Embedding error (attempt {attempt + 1}): {str(e)}")
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
        
        raise Exception("Failed to get embedding after all retries")
    
    async def get_embeddings_batch(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Get embeddings for multiple texts with batching.
        
        Args:
            texts: List of texts to embed
            model: Embedding model
            
        Returns:
            List of embedding vectors
        """
        model = model or settings.OPENROUTER_EMBEDDING_MODEL
        
        if not texts:
            return []
        
        embeddings = []
        batch_size = 10  # Smaller batches for reliability
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Clean batch texts
            clean_batch = []
            for text in batch:
                text = text.strip() if text else ""
                if len(text) > 30000:
                    text = text[:30000]
                clean_batch.append(text if text else " ")  # Replace empty with space
            
            payload = {
                "model": model,
                "input": clean_batch
            }
            
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=90.0, verify=False) as client:
                        response = await client.post(
                            f"{self.base_url}/embeddings",
                            headers=self.headers,
                            json=payload
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        batch_embeddings = [item["embedding"] for item in result["data"]]
                        embeddings.extend(batch_embeddings)
                        break
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        wait_time = 2 ** attempt
                        logger.warning(f"Batch embedding rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Batch embedding error: {e.response.text}")
                        # Don't add zero vectors - let the caller handle None
                        raise
                        
                except Exception as e:
                    logger.error(f"Batch embedding error: {str(e)}")
                    if attempt == 2:
                        # Don't add zero vectors on final failure - raise instead
                        raise
                    await asyncio.sleep(1)
        
        return embeddings
    
    async def analyze_legal_document(
        self,
        document_text: str,
        analysis_type: str = "full",
        contract_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform deep legal analysis using reasoning model.
        
        Args:
            document_text: Full document text
            analysis_type: Type of analysis ('full', 'risks', 'clauses', 'summary')
            contract_type: Optional contract type for specialized analysis
            
        Returns:
            Structured analysis results
        """
        system_prompt = """You are an expert legal analyst specializing in contract review.
You MUST provide analysis in valid JSON format ONLY. No explanatory text outside JSON.

CRITICAL RULES:
1. ONLY analyze what is explicitly present in the document
2. NEVER infer or assume information not stated
3. Rate confidence for each finding (high/medium/low)
4. Cite specific text for every claim
5. Flag any ambiguous or unclear language
"""

        analysis_prompts = {
            "full": f"""Analyze this contract comprehensively. Return JSON with this exact structure:
{{
    "summary": "Brief executive summary (2-3 sentences)",
    "contract_type": "Detected contract type",
    "parties": ["List of parties identified"],
    "key_dates": [{{"description": "...", "date": "...", "confidence": "high/medium/low"}}],
    "key_clauses": [
        {{
            "name": "Clause name",
            "content_summary": "What it says",
            "risk_level": "low/medium/high/critical",
            "location": "Where in document",
            "concerns": ["Any issues"],
            "confidence": "high/medium/low"
        }}
    ],
    "risks": [
        {{
            "severity": "low/medium/high/critical",
            "description": "Risk description",
            "affected_clause": "Which clause",
            "recommendation": "How to address",
            "confidence": "high/medium/low"
        }}
    ],
    "missing_elements": ["Standard elements not found"],
    "compliance_status": {{
        "overall": "compliant/needs_review/non_compliant",
        "checks": {{"element": "status"}}
    }},
    "recommendations": ["Actionable recommendations"],
    "overall_risk_score": 0.0-1.0,
    "confidence_level": "high/medium/low"
}}

Contract Type Hint: {contract_type or 'Unknown'}

DOCUMENT:
{document_text[:50000]}""",

            "risks": f"""Identify ALL risks in this contract. Return JSON:
{{
    "risks": [
        {{
            "severity": "low/medium/high/critical",
            "category": "financial/legal/operational/compliance/reputational",
            "description": "Detailed risk description",
            "source_text": "Exact quote from document",
            "location": "Section/paragraph reference",
            "impact": "Potential consequences",
            "likelihood": "low/medium/high",
            "recommendation": "Mitigation suggestion",
            "confidence": "high/medium/low"
        }}
    ],
    "overall_risk_level": "low/medium/high/critical",
    "risk_score": 0.0-1.0,
    "priority_actions": ["Top 3 actions needed"]
}}

DOCUMENT:
{document_text[:50000]}""",

            "clauses": f"""Extract and analyze ALL clauses. Return JSON:
{{
    "clauses": [
        {{
            "name": "Standard clause name",
            "category": "payment/termination/liability/confidentiality/ip/dispute/indemnification/warranty/force_majeure/other",
            "content": "Full clause text",
            "summary": "Plain language summary",
            "is_standard": true/false,
            "deviations": "How it differs from standard",
            "risk_level": "low/medium/high/critical",
            "negotiability": "non_negotiable/negotiable/highly_negotiable",
            "related_clauses": ["Other related clauses"],
            "confidence": "high/medium/low"
        }}
    ],
    "clause_coverage": {{
        "present": ["Standard clauses found"],
        "missing": ["Expected but not found"],
        "unusual": ["Non-standard clauses"]
    }}
}}

DOCUMENT:
{document_text[:50000]}""",

            "summary": f"""Provide executive summary. Return JSON:
{{
    "title": "Contract title/name",
    "type": "Contract type",
    "parties": [{{"name": "...", "role": "..."}}],
    "effective_date": "Date or null",
    "term": "Duration/term",
    "value": "Financial value if stated",
    "purpose": "Main purpose in 1-2 sentences",
    "key_obligations": [
        {{"party": "...", "obligation": "..."}}
    ],
    "critical_dates": [{{"event": "...", "date": "..."}}],
    "special_conditions": ["Notable conditions"],
    "executive_summary": "3-5 sentence summary for executives",
    "confidence": "high/medium/low"
}}

DOCUMENT:
{document_text[:30000]}"""
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["full"])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.chat_completion(
                messages=messages,
                model_type="reasoning",
                temperature=0.0,  # Maximum consistency for legal analysis
                max_tokens=4000
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                else:
                    json_str = content
                
                result = json.loads(json_str.strip())
                result["model_used"] = response.get("model_used", "unknown")
                result["analysis_type"] = analysis_type
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse analysis JSON: {str(e)}")
                return {
                    "error": "Failed to parse analysis",
                    "raw_response": content,
                    "analysis_type": analysis_type
                }
                
        except Exception as e:
            logger.error(f"Legal analysis error: {str(e)}")
            return {
                "error": str(e),
                "analysis_type": analysis_type
            }


# Global OpenRouter client instance
openrouter_client = OpenRouterClient()
