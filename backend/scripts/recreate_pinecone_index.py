"""
Script to recreate Pinecone index with 1536 dimensions.
This will:
1. Backup existing vectors (optional)
2. Delete old index
3. Create new index with 1536 dimensions
4. Re-index all documents from database
"""
import sys
from pathlib import Path
import asyncio
import logging

# Add app to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.crud.upload import get_uploads
from app.schemas.upload import UploadFilters
from app.db.models.upload import ExtractionStatus
from app.services.pinecone_client import pinecone_client
from app.services.indexing import index_file_to_pinecone
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def recreate_index():
    """Recreate Pinecone index with correct dimensions."""
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("Pinecone Index Recreation Script")
        logger.info("=" * 60)
        
        # Step 1: Connect to Pinecone
        logger.info("\n[1/5] Connecting to Pinecone...")
        if not pinecone_client.connect():
            logger.error("Failed to connect to Pinecone!")
            return False
        logger.info("✅ Connected to Pinecone")
        
        # Step 2: Get index stats
        logger.info("\n[2/5] Checking current index...")
        try:
            stats = pinecone_client.get_index_stats()
            current_count = stats.get("total_vector_count", 0)
            logger.info(f"Current index has {current_count} vectors")
        except Exception as e:
            logger.warning(f"Could not get index stats: {e}")
            current_count = 0
        
        # Step 3: Delete old index
        logger.info("\n[3/5] Deleting old index...")
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists
            existing_indexes = pc.list_indexes()
            if settings.PINECONE_INDEX_NAME in [idx.name for idx in existing_indexes]:
                logger.info(f"Deleting index: {settings.PINECONE_INDEX_NAME}")
                pc.delete_index(settings.PINECONE_INDEX_NAME)
                logger.info("✅ Old index deleted")
                
                # Wait a bit for deletion to complete
                import time
                logger.info("Waiting 10 seconds for index deletion to complete...")
                time.sleep(10)
            else:
                logger.info("Index doesn't exist, skipping deletion")
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False
        
        # Step 4: Create new index with 1536 dimensions
        logger.info("\n[4/5] Creating new index with 1536 dimensions...")
        try:
            from pinecone import ServerlessSpec
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=1536,  # New dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.PINECONE_ENVIRONMENT
                )
            )
            logger.info("✅ New index created with 1536 dimensions")
            
            # Wait for index to be ready
            import time
            logger.info("Waiting 30 seconds for index to be ready...")
            time.sleep(30)
            
            # Reconnect
            pinecone_client.connect()
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
        
        # Step 5: Re-index all documents
        logger.info("\n[5/5] Re-indexing all documents...")
        
        # Get all successfully extracted uploads in batches
        all_uploads = []
        batch_size = 500  # Max allowed by schema
        skip = 0
        
        while True:
            filters = UploadFilters(
                status=ExtractionStatus.COMPLETED,
                skip=skip,
                limit=batch_size
            )
            batch = get_uploads(db, filters)
            if not batch:
                break
            all_uploads.extend(batch)
            skip += batch_size
            if len(batch) < batch_size:
                break
        
        logger.info(f"Found {len(all_uploads)} documents to re-index")
        
        success_count = 0
        fail_count = 0
        
        for i, upload in enumerate(all_uploads, 1):
            logger.info(f"\n[{i}/{len(all_uploads)}] Indexing: {upload.filename} (ID: {upload.id})")
            try:
                result = await index_file_to_pinecone(db, upload.id)
                if result:
                    success_count += 1
                    logger.info(f"✅ Successfully indexed {upload.filename}")
                else:
                    fail_count += 1
                    logger.warning(f"⚠️ Failed to index {upload.filename}")
            except Exception as e:
                fail_count += 1
                logger.error(f"❌ Error indexing {upload.filename}: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Re-indexing Complete!")
        logger.info(f"✅ Successfully indexed: {success_count}")
        logger.info(f"❌ Failed: {fail_count}")
        logger.info("=" * 60)
        
        # Verify new index
        try:
            stats = pinecone_client.get_index_stats()
            new_count = stats.get("total_vector_count", 0)
            logger.info(f"\nNew index has {new_count} vectors")
        except Exception as e:
            logger.warning(f"Could not verify index stats: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Recreate Pinecone index with 1536 dimensions")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    if not args.yes:
        print("\n⚠️  WARNING: This will delete the existing Pinecone index and recreate it!")
        print("All existing vectors will be lost and re-indexed from the database.")
        print("\nMake sure you have:")
        print("1. All documents properly extracted in the database")
        print("2. Backed up any important data")
        print("3. Confirmed you want to proceed\n")
        
        response = input("Type 'YES' to proceed: ")
        if response != "YES":
            print("Cancelled.")
            sys.exit(0)
    
    success = asyncio.run(recreate_index())
    if success:
        print("\n✅ Index recreation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Index recreation failed. Check logs above.")
        sys.exit(1)

