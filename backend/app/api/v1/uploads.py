"""
Upload endpoints for file management.
Handles file uploads, downloads, and text extraction.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List
import mimetypes
from pathlib import Path
import json

from app.db.session import get_db
from app.db.crud.upload import (
    get_upload,
    get_uploads,
    create_upload,
    delete_upload,
    extract_and_save_text
)
from app.schemas.upload import Upload as UploadSchema, UploadListItem, UploadFilters, ExtractedText
from app.db.models.upload import FileType, ExtractionStatus
from app.db.models.user import User
from app.api.deps import get_current_user
from app.services.storage import storage
from app.core.config import settings
from app.core.errors import NotFoundException, BadRequestException

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIMETYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}


def get_file_type(filename: str) -> FileType:
    """Determine file type from filename."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return FileType.PDF
    elif ext == ".docx":
        return FileType.DOCX
    elif ext == ".txt":
        return FileType.TXT
    return FileType.OTHER


@router.post("", response_model=UploadSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file.
    
    Args:
        file: File to upload
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Upload record with metadata
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Upload request received: filename={file.filename}, content_type={file.content_type}, user={current_user.id}")
    
    # Validate filename
    if not file.filename:
        logger.error("Upload failed: No filename provided")
        raise BadRequestException(detail="Filename is required")
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.error(f"Upload failed: Invalid file extension {file_ext}")
        raise BadRequestException(
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"File read successfully: {file_size} bytes")
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Validate file size
    if file_size == 0:
        logger.error("Upload failed: File is empty")
        raise BadRequestException(detail="File is empty")
    
    if file_size > settings.FILE_MAX_SIZE:
        max_mb = settings.FILE_MAX_SIZE / (1024 * 1024)
        logger.error(f"Upload failed: File too large ({file_size} bytes > {settings.FILE_MAX_SIZE} bytes)")
        raise BadRequestException(
            detail=f"File too large. Maximum size: {max_mb}MB"
        )
    
    # Save file to storage
    file_path = None
    try:
        from io import BytesIO
        file_obj = BytesIO(file_content)
        file_path = storage.save_file(file_obj, file.filename, "uploads")
        logger.info(f"File saved to: {file_path}")
        
        # Verify file was saved
        if not storage.file_exists(file_path):
            raise Exception("File was not saved correctly - file does not exist after save")
        logger.info("File existence verified")
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Determine file type
    file_type = get_file_type(file.filename)
    logger.info(f"File type determined: {file_type}")
    
    # Create upload record
    try:
        db_upload = create_upload(
            db=db,
            filename=file.filename,
            file_type=file_type,
            path=file_path,
            size=file_size,
            user_id=current_user.id,
            mime_type=file.content_type
        )
        logger.info(f"Created upload record: {db_upload.id}")
    except Exception as e:
        logger.error(f"Failed to create upload record: {str(e)}", exc_info=True)
        # Try to clean up saved file
        if file_path:
            try:
                storage.delete_file(file_path)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file: {cleanup_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create upload record: {str(e)}"
        )
    
    # Start text extraction and indexing (async, don't block response)
    if file_type in [FileType.PDF, FileType.DOCX, FileType.TXT]:
        try:
            # Extract text synchronously
            extraction_success = extract_and_save_text(db, db_upload.id)
            logger.info(f"Extraction result for {db_upload.id}: {extraction_success}")
            
            # If extraction succeeded, index to Pinecone
            if extraction_success:
                # Refresh to get updated status
                db.refresh(db_upload)
                
                # Index to Pinecone for RAG (await it properly)
                try:
                    from app.services.indexing import index_file_to_pinecone
                    indexing_result = await index_file_to_pinecone(db, db_upload.id)
                    if indexing_result:
                        logger.info(f"Successfully indexed file {db_upload.id} to Pinecone")
                    else:
                        logger.warning(f"Indexing returned False for file {db_upload.id}")
                except Exception as e:
                    # Log but don't fail - indexing can be retried
                    logger.error(f"Auto-indexing failed for {db_upload.id}: {e}", exc_info=True)
            else:
                logger.warning(f"Text extraction failed for {db_upload.id}")
        except Exception as e:
            # Log but don't fail upload - extraction can be retried
            logger.error(f"Error during extraction/indexing for {db_upload.id}: {e}", exc_info=True)
    
    # Return upload record
    try:
        result = UploadSchema.model_validate(db_upload)
        logger.info(f"Upload completed successfully: {db_upload.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to serialize upload response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload response: {str(e)}"
        )


@router.get("", response_model=List[UploadListItem])
async def list_uploads(
    skip: int = 0,
    limit: int = 100,
    file_type: FileType = None,
    status: ExtractionStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List uploaded files with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        file_type: Filter by file type
        status: Filter by extraction status
        db: Database session
        current_user: Current user
        
    Returns:
        List of upload records
    """
    filters = UploadFilters(
        skip=skip,
        limit=limit,
        file_type=file_type,
        status=status,
        uploaded_by=current_user.id  # Users can only see their own files
    )
    
    uploads = get_uploads(db, filters)
    return [UploadListItem.model_validate(u) for u in uploads]


@router.get("/{upload_id}", response_model=UploadSchema)
async def get_upload_details(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upload details by ID.
    
    Args:
        upload_id: Upload ID
        db: Database session
        current_user: Current user
        
    Returns:
        Upload record
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        raise NotFoundException(detail="Upload not found")
    
    # Verify ownership
    if db_upload.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file"
        )
    
    return UploadSchema.model_validate(db_upload)


@router.get("/{upload_id}/download")
async def download_file(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a file.
    
    Args:
        upload_id: Upload ID
        db: Database session
        current_user: Current user
        
    Returns:
        File stream
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        raise NotFoundException(detail="Upload not found")
    
    # Verify ownership
    if db_upload.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file"
        )
    
    # Get file path
    file_path = storage.get_file_path(db_upload.path)
    if not file_path.exists():
        raise NotFoundException(detail="File not found on disk")
    
    # Return file
    return FileResponse(
        path=str(file_path),
        filename=db_upload.filename,
        media_type=db_upload.mime_type or "application/octet-stream"
    )


@router.get("/{upload_id}/text", response_model=ExtractedText)
async def get_extracted_text(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get extracted text from a file.
    
    Args:
        upload_id: Upload ID
        db: Database session
        current_user: Current user
        
    Returns:
        Extracted text and chunks
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        raise NotFoundException(detail="Upload not found")
    
    # Verify ownership
    if db_upload.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this file"
        )
    
    # Check extraction status
    if db_upload.text_extraction_status == ExtractionStatus.PENDING:
        return ExtractedText(
            file_id=db_upload.id,
            status=ExtractionStatus.PENDING,
            pages_count=None,
            text=None,
            chunks=None
        )
    elif db_upload.text_extraction_status == ExtractionStatus.PROCESSING:
        return ExtractedText(
            file_id=db_upload.id,
            status=ExtractionStatus.PROCESSING,
            pages_count=None,
            text=None,
            chunks=None
        )
    elif db_upload.text_extraction_status == ExtractionStatus.FAILED:
        return ExtractedText(
            file_id=db_upload.id,
            status=ExtractionStatus.FAILED,
            error="Text extraction failed"
        )
    
    # Get extracted text
    if not db_upload.extracted_text_path:
        raise NotFoundException(detail="Extracted text not found")
    
    text_content = storage.read_file(db_upload.extracted_text_path)
    if not text_content:
        raise NotFoundException(detail="Extracted text file not found")
    
    # Parse JSON
    try:
        extraction_data = json.loads(text_content.decode("utf-8"))
        return ExtractedText(
            file_id=db_upload.id,
            status=ExtractionStatus.COMPLETED,
            pages_count=db_upload.pages_count,
            text=extraction_data.get("full_text"),
            chunks=extraction_data.get("chunks", [])
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse extracted text"
        )


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload_file(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an uploaded file.
    
    Args:
        upload_id: Upload ID
        db: Database session
        current_user: Current user
    """
    db_upload = get_upload(db, upload_id)
    if not db_upload:
        raise NotFoundException(detail="Upload not found")
    
    # Verify ownership
    if db_upload.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this file"
        )
    
    # Delete upload
    delete_upload(db, upload_id)
    return None
