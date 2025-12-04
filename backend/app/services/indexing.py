"""
Helper functions for indexing uploaded files into Pinecone vector store.
This connects the upload pipeline with the RAG system.
"""
from sqlalchemy.orm import Session
from uuid import UUID
import json
import logging

from app.db.crud.upload import get_upload
from app.services.storage import storage
from app.services.embedding import embedding_service
from app.services.pinecone_client import pinecone_client
from app.db.models.upload import ExtractionStatus

logger = logging.getLogger(__name__)


async def index_file_to_pinecone(
    db: Session,
    upload_id: UUID
) -> bool:
    """
    Index an uploaded file's chunks into Pinecone.
    
    This function:
    1. Retrieves extracted text + chunks
    2. Generates embeddings for each chunk
    3. Upserts vectors to Pinecone with metadata
    
    Args:
        db: Database session
        upload_id: Upload ID to index
        
    Returns:
        True if successful, False otherwise
    """
    # Get upload record
    upload = get_upload(db, upload_id)
    if not upload:
        logger.error(f"Upload {upload_id} not found")
        return False
    
    # Check extraction status
    if upload.text_extraction_status != ExtractionStatus.COMPLETED:
        logger.warning(f"Upload {upload_id} extraction not completed (status: {upload.text_extraction_status})")
        return False
    
    # Get extracted text file
    if not upload.extracted_text_path:
        logger.error(f"Upload {upload_id} has no extracted text path")
        return False
    
    try:
        # Load extracted text JSON
        text_content = storage.read_file(upload.extracted_text_path)
        if not text_content:
            logger.error(f"Could not read extracted text for upload {upload_id}")
            return False
        
        extraction_data = json.loads(text_content.decode("utf-8"))
        chunks = extraction_data.get("chunks", [])
        
        if not chunks:
            logger.warning(f"No chunks found for upload {upload_id}")
            return False
        
        logger.info(f"Indexing {len(chunks)} chunks for upload {upload_id}")
        
        # Generate embeddings for all chunks
        enriched_chunks = await embedding_service.embed_chunks(chunks)
        
        # Get index dimension to ensure compatibility
        try:
            index_stats = pinecone_client.get_index_stats()
            # Check if we can determine dimension from stats
            # If index exists, we need to match its dimension
            logger.info(f"Pinecone index stats: {index_stats}")
        except:
            pass
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, chunk in enumerate(enriched_chunks):
            if not chunk.get("has_embedding"):
                logger.warning(f"Chunk {i} for upload {upload_id} has no embedding, skipping")
                continue
            
            embedding = chunk["embedding"]
            
            # Skip if embedding is None or empty
            if not embedding or len(embedding) == 0:
                logger.error(f"Chunk {i} has no embedding, skipping")
                continue
            
            # Check if embedding is all zeros (indicates failure)
            if all(v == 0.0 for v in embedding):
                logger.error(f"Chunk {i} has zero embedding (embedding generation likely failed), skipping")
                continue
            
            # Verify embedding dimension matches index (should be 1536)
            if len(embedding) != 1536:
                logger.warning(f"Chunk {i} has unexpected embedding dimension: {len(embedding)} (expected 1536)")
                if len(embedding) > 1536:
                    # For larger embeddings, take first 1536 (simple truncation)
                    embedding = embedding[:1536]
                    logger.warning(f"Truncated embedding to 1536 dimensions")
                elif len(embedding) < 1536:
                    # For smaller embeddings, pad with zeros (not ideal but prevents errors)
                    embedding = embedding + [0.0] * (1536 - len(embedding))
                    logger.warning(f"Padded embedding to 1536 dimensions")
            
            # Create vector ID
            vector_id = f"{upload_id}_chunk_{i}"
            
            # Prepare metadata with enhanced information
            metadata = {
                "file_id": str(upload_id),
                "filename": upload.filename,
                "text": chunk["text"][:1000],  # Limit text length for metadata
                "chunk_index": i,
                "char_count": chunk.get("char_count", len(chunk.get("text", "")))
            }
            
            # Add page info if available
            if chunk.get("metadata", {}).get("page"):
                metadata["page"] = chunk["metadata"]["page"]
            
            # Add section title if available (from enhanced chunking)
            if chunk.get("section_title"):
                metadata["section_title"] = chunk["section_title"]
            
            # Add detected clauses if available
            if chunk.get("detected_clauses"):
                metadata["detected_clauses"] = chunk["detected_clauses"]
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert to Pinecone
        if vectors:
            success = pinecone_client.upsert_vectors(vectors)
            if success:
                logger.info(f"Successfully indexed {len(vectors)} vectors for upload {upload_id}")
                return True
            else:
                logger.error(f"Failed to upsert vectors for upload {upload_id}")
                return False
        else:
            logger.warning(f"No valid vectors to index for upload {upload_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error indexing upload {upload_id}: {str(e)}")
        return False


async def delete_file_from_pinecone(upload_id: UUID) -> bool:
    """
    Delete all vectors for a file from Pinecone.
    
    Args:
        upload_id: Upload ID
        
    Returns:
        True if successful
    """
    try:
        # Generate all possible vector IDs for this file
        # This is a simplified approach - in production, you might query first
        # For now, we'll delete up to 1000 possible chunks
        vector_ids = [f"{upload_id}_chunk_{i}" for i in range(1000)]
        
        success = pinecone_client.delete_vectors(vector_ids)
        if success:
            logger.info(f"Deleted vectors for upload {upload_id}")
        return success
        
    except Exception as e:
        logger.error(f"Error deleting vectors for upload {upload_id}: {str(e)}")
        return False
