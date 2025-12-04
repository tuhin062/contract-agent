"""
Diagnostic script to check Pinecone index status and verify documents are indexed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pinecone_client import pinecone_client
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_pinecone():
    """Check Pinecone index status."""
    print("=" * 60)
    print("Pinecone Index Diagnostic")
    print("=" * 60)
    
    # Connect to Pinecone
    print("\n1. Connecting to Pinecone...")
    if not pinecone_client.connect():
        print("❌ Failed to connect to Pinecone")
        return False
    print("✅ Connected to Pinecone")
    
    # Get index stats
    print("\n2. Getting index statistics...")
    stats = pinecone_client.get_index_stats()
    print(f"Index Name: {settings.PINECONE_INDEX_NAME}")
    print(f"Namespace: {settings.PINECONE_NAMESPACE}")
    print(f"Total Vectors: {stats.get('total_vector_count', 'N/A')}")
    print(f"Namespaces: {stats.get('namespaces', {})}")
    
    # Test query with a simple query
    print("\n3. Testing query with sample text...")
    from app.services.embedding import embedding_service
    import asyncio
    
    async def test_query():
        test_query = "test document"
        embedding = await embedding_service.generate_embedding(test_query)
        if embedding:
            print(f"✅ Generated embedding: dimension={len(embedding)}")
            
            # Query Pinecone
            results = pinecone_client.query_vectors(
                query_vector=embedding,
                top_k=5,
                filter_dict=None
            )
            print(f"✅ Query returned {len(results)} results")
            
            if results:
                print("\nTop results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"  {i}. Score: {result['score']:.3f}")
                    if result.get('metadata'):
                        print(f"     File ID: {result['metadata'].get('file_id', 'N/A')}")
                        print(f"     Filename: {result['metadata'].get('filename', 'N/A')}")
                        print(f"     Text preview: {result['metadata'].get('text', '')[:100]}...")
            else:
                print("⚠️  No results found - index may be empty or query didn't match")
        else:
            print("❌ Failed to generate embedding")
    
    asyncio.run(test_query())
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    return True

if __name__ == "__main__":
    check_pinecone()

