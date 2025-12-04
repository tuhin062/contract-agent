"""
CRUD operations for Upload model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
import json
from pathlib import Path

from app.db.models.upload import Upload, FileType, ExtractionStatus
from app.schemas.upload import UploadFilters
from app.services.storage import storage
from app.services.extraction import text_extractor
from app.services.chunking import chunking_service
from app.services.chunking_enhanced import enhanced_chunking_service


def get_upload(db: Session, upload_id: UUID) -> Optional[Upload]:
    """Get upload by ID."""
    return db.query(Upload).filter(Upload.id == upload_id).first()


def get_uploads(
    db: Session,
    filters: UploadFilters
) -> List[Upload]:
    """
    Get list of uploads with filters.
    
    Args:
        db: Database session
        filters: Upload filters (type, status, user, pagination)
    """
    query = db.query(Upload)
    
    if filters.file_type:
        query = query.filter(Upload.file_type == filters.file_type)
    if filters.status:
        query = query.filter(Upload.text_extraction_status == filters.status)
    if filters.uploaded_by:
        query = query.filter(Upload.uploaded_by == filters.uploaded_by)
    
    return query.order_by(Upload.uploaded_at.desc()).offset(filters.skip).limit(filters.limit).all()


def create_upload(
    db: Session,
    filename: str,
    file_type: FileType,
    path: str,
    size: int,
    user_id: UUID,
    mime_type: Optional[str] = None,
    metadata: dict = None
) -> Upload:
    """
    Create a new upload record.
    
    Args:
        db: Database session
        filename: Original filename
        file_type: Type of file
        path: Storage path
        size: File size in bytes
        user_id: ID of user who uploaded
        mime_type: MIME type
        metadata: Additional metadata
    """
    db_upload = Upload(
        filename=filename,
        file_type=file_type,
        path=path,
        size=size,
        uploaded_by=user_id,
        mime_type=mime_type,
        metadata=metadata or {},
        text_extraction_status=ExtractionStatus.PENDING
    )
    
    db.add(db_upload)
    db.commit()
    db.refresh(db_upload)
    return db_upload


def update_extraction_status(
    db: Session,
    upload_id: UUID,
    status: ExtractionStatus,
    pages_count: Optional[int] = None,
    extracted_text_path: Optional[str] = None
) -> Optional[Upload]:
    """
    Update extraction status for an upload.
    
    Args:
        db: Database session
        upload_id: Upload ID
        status: New extraction status
        pages_count: Number of pages (for PDFs)
        extracted_text_path: Path to extracted text file
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        return None
    
    db_upload.text_extraction_status = status
    if pages_count is not None:
        db_upload.pages_count = pages_count
    if extracted_text_path:
        db_upload.extracted_text_path = extracted_text_path
    
    db.commit()
    db.refresh(db_upload)
    return db_upload


def delete_upload(db: Session, upload_id: UUID) -> bool:
    """
    Delete an upload and its associated files.
    
    Args:
        db: Database session
        upload_id: Upload ID
        
    Returns:
        True if deleted, False if not found
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        return False
    
    # Delete physical file
    storage.delete_file(db_upload.path)
    
    # Delete extracted text if exists
    if db_upload.extracted_text_path:
        storage.delete_file(db_upload.extracted_text_path)
    
    # Delete database record
    db.delete(db_upload)
    db.commit()
    return True


def extract_and_save_text(db: Session, upload_id: UUID) -> bool:
    """
    Extract text from uploaded file and save it.
    
    Args:
        db: Database session
        upload_id: Upload ID
        
    Returns:
        True if successful, False otherwise
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        return False
    
    # Update status to processing
    update_extraction_status(db, upload_id, ExtractionStatus.PROCESSING)
    
    try:
        # Get file path
        file_path = storage.get_file_path(db_upload.path)
        
        # Extract text
        result = text_extractor.extract_text(file_path, db_upload.file_type.value)
        
        if not result.get("success"):
            # Extraction failed
            update_extraction_status(db, upload_id, ExtractionStatus.FAILED)
            return False
        
        # Create chunks if we have text using enhanced chunking
        full_text = result.get("full_text", "")
        chunks = []
        
        if "pages" in result:
            # PDF - chunk by pages with enhanced chunking
            chunks = enhanced_chunking_service.chunk_by_pages(
                result["pages"],
                file_id=str(upload_id)
            )
        elif full_text:
            # Other formats - chunk the full text with enhanced chunking
            chunks = enhanced_chunking_service.chunk_document(
                full_text,
                metadata={"file_id": str(upload_id)}
            )
        
        # Save extraction results as JSON
        extraction_data = {
            "file_id": str(upload_id),
            "filename": db_upload.filename,
            "full_text": full_text,
            "chunks": chunks,
            "metadata": result.get("metadata", {})
        }
        
        # Save to storage
        extraction_filename = f"{upload_id}_extracted.json"
        extraction_json = json.dumps(extraction_data, indent=2)
        extracted_path = storage.save_text(
            extraction_json,
            extraction_filename,
            file_type="processed"
        )
        
        # Update upload record
        pages_count = result.get("pages_count", len(chunks))
        update_extraction_status(
            db,
            upload_id,
            ExtractionStatus.COMPLETED,
            pages_count=pages_count,
            extracted_text_path=extracted_path
        )
        
        return True
    
    except Exception as e:
        # Extraction failed
        update_extraction_status(db, upload_id, ExtractionStatus.FAILED)
        return False
