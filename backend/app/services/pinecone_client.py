"""
Pinecone vector store client for document embeddings.
Handles connection, indexing, and querying operations.
"""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class PineconeClient:
    """Client for interacting with Pinecone vector database."""
    
    def __init__(self):
        """Initialize Pinecone client."""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.namespace = settings.PINECONE_NAMESPACE
        self.index = None
        
    def connect(self):
        """Connect to Pinecone index."""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            
            if self.index_name not in [idx.name for idx in existing_indexes]:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                # Create index if it doesn't exist
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embedding dimension (text-embedding-ada-002, text-embedding-3-small)
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
                logger.info(f"Index {self.index_name} created successfully with 1536 dimensions")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone connection error: {str(e)}")
            return False
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of vector dictionaries with id, values, and metadata
            namespace: Optional namespace (defaults to configured namespace)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            self.connect()
        
        try:
            ns = namespace or self.namespace
            
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch, namespace=ns)
            
            logger.info(f"Upserted {len(vectors)} vectors to namespace '{ns}'")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            return False
    
    def query_vectors(
        self,
        query_vector: List[float],
        top_k: int = 8,
        filter_dict: Optional[Dict] = None,
        namespace: Optional[str] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Query similar vectors from Pinecone.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            namespace: Optional namespace
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matching vectors with scores and metadata
        """
        if not self.index:
            self.connect()
        
        try:
            ns = namespace or self.namespace
            
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                namespace=ns,
                include_metadata=include_metadata
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata if include_metadata else None
                })
            
            logger.info(f"Query returned {len(matches)} results from namespace '{ns}'")
            return matches
            
        except Exception as e:
            logger.error(f"Pinecone query error: {str(e)}")
            return []
    
    def delete_vectors(
        self,
        ids: List[str],
        namespace: Optional[str] = None
    ) -> bool:
        """
        Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
            
        Returns:
            True if successful
        """
        if not self.index:
            self.connect()
        
        try:
            ns = namespace or self.namespace
            self.index.delete(ids=ids, namespace=ns)
            logger.info(f"Deleted {len(ids)} vectors from namespace '{ns}'")
            return True
            
        except Exception as e:
            logger.error(f"Pinecone delete error: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get index statistics."""
        if not self.index:
            self.connect()
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}


# Global Pinecone client instance
pinecone_client = PineconeClient()
