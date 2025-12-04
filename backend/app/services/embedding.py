"""
Embedding service for generating and managing text embeddings.
Integrates with OpenRouter for embedding generation.
"""
from typing import List, Dict, Optional
import logging
from app.services.openrouter import openrouter_client

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.client = openrouter_client
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        try:
            embedding = await self.client.get_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return None
    
    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return [None] * len(texts)
        
        try:
            embeddings = await self.client.get_embeddings_batch(valid_texts)
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation error: {str(e)}")
            return [None] * len(texts)
    
    async def embed_chunks(
        self,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            List of chunks with added 'embedding' field
        """
        if not chunks:
            return []
        
        # Extract texts
        texts = [chunk.get("text", "") for chunk in chunks]
        
        # Generate embeddings
        embeddings = await self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        enriched_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            enriched_chunk = chunk.copy()
            enriched_chunk["embedding"] = embedding
            enriched_chunk["has_embedding"] = embedding is not None
            enriched_chunks.append(enriched_chunk)
        
        # Log statistics
        success_count = sum(1 for c in enriched_chunks if c["has_embedding"])
        logger.info(
            f"Generated embeddings for {success_count}/{len(chunks)} chunks"
        )
        
        return enriched_chunks


# Global embedding service instance
embedding_service = EmbeddingService()
