"""
Background task definitions for RQ workers.
"""
import logging
from uuid import UUID
from typing import Optional

from app.db.session import SessionLocal
from app.db.crud.upload import get_upload, extract_and_save_text
from app.db.crud.proposal import update_proposal_status, update_proposal_validation, fail_proposal_validation
from app.db.crud.audit import create_audit_log
from app.db.models.upload import ExtractionStatus
from app.db.models.proposal import ValidationStatus, RiskLevel
from app.db.models.audit import AuditAction
from app.services.indexing import index_file_to_pinecone
from app.services.validation import validation_service

logger = logging.getLogger(__name__)


async def process_file_upload(upload_id: str, user_id: str):
    """
    Background task to process an uploaded file.
    
    1. Extract text from file
    2. Chunk the text
    3. Generate embeddings
    4. Index to Pinecone
    
    Args:
        upload_id: ID of the upload
        user_id: ID of the user who uploaded
    """
    db = SessionLocal()
    try:
        upload_uuid = UUID(upload_id)
        user_uuid = UUID(user_id)
        
        logger.info(f"Processing upload {upload_id}")
        
        # Check upload exists
        upload = get_upload(db, upload_uuid)
        if not upload:
            logger.error(f"Upload {upload_id} not found")
            return {"success": False, "error": "Upload not found"}
        
        # Extract text
        extraction_success = extract_and_save_text(db, upload_uuid)
        if not extraction_success:
            logger.error(f"Text extraction failed for {upload_id}")
            return {"success": False, "error": "Text extraction failed"}
        
        # Index to Pinecone
        indexing_success = await index_file_to_pinecone(db, upload_uuid)
        if not indexing_success:
            logger.warning(f"Indexing failed for {upload_id}")
            # Don't fail the task - file is still usable without indexing
        
        # Audit log
        create_audit_log(
            db=db,
            action=AuditAction.FILE_INDEXED if indexing_success else AuditAction.FILE_UPLOADED,
            description=f"File processed: {upload.filename}",
            user_id=user_uuid,
            resource_type="upload",
            resource_id=upload_uuid,
            details={
                "filename": upload.filename,
                "indexed": indexing_success,
                "extraction_status": upload.text_extraction_status.value
            }
        )
        
        logger.info(f"Successfully processed upload {upload_id}")
        return {"success": True, "indexed": indexing_success}
        
    except Exception as e:
        logger.error(f"Error processing upload {upload_id}: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


async def validate_contract_background(
    contract_id: str,
    proposal_id: str,
    contract_text: str,
    contract_type: Optional[str],
    user_id: str
):
    """
    Background task to validate a contract.
    
    Args:
        contract_id: ID of the contract
        proposal_id: ID of the proposal to update
        contract_text: Full contract text
        contract_type: Type of contract
        user_id: ID of the user
    """
    db = SessionLocal()
    try:
        proposal_uuid = UUID(proposal_id)
        user_uuid = UUID(user_id)
        
        logger.info(f"Validating contract {contract_id}")
        
        # Update status to in-progress
        update_proposal_status(db, proposal_uuid, ValidationStatus.IN_PROGRESS)
        
        # Run validation
        validation_result = await validation_service.validate_contract(
            contract_text=contract_text,
            contract_type=contract_type
        )
        
        # Map risk level
        risk_level_map = {
            "LOW": RiskLevel.LOW,
            "MEDIUM": RiskLevel.MEDIUM,
            "HIGH": RiskLevel.HIGH,
            "CRITICAL": RiskLevel.CRITICAL
        }
        risk_level = risk_level_map.get(
            validation_result.get("risk_level", "MEDIUM").upper(),
            RiskLevel.MEDIUM
        )
        
        # Update proposal with results
        update_proposal_validation(
            db=db,
            proposal_id=proposal_uuid,
            risk_score=validation_result.get("risk_score", 0.5),
            risk_level=risk_level,
            validation_report=validation_result,
            detected_clauses=validation_result.get("clauses", []),
            compliance_checks=validation_result.get("compliance", {})
        )
        
        # Audit log
        create_audit_log(
            db=db,
            action=AuditAction.VALIDATION_COMPLETED,
            description=f"Contract validation completed",
            user_id=user_uuid,
            resource_type="proposal",
            resource_id=proposal_uuid,
            details={
                "contract_id": contract_id,
                "risk_level": risk_level.value,
                "risk_score": validation_result.get("risk_score")
            }
        )
        
        logger.info(f"Validation completed for contract {contract_id}")
        return {"success": True, "risk_level": risk_level.value}
        
    except Exception as e:
        logger.error(f"Validation error for contract {contract_id}: {str(e)}")
        
        # Mark as failed
        try:
            fail_proposal_validation(db, proposal_uuid, str(e))
            
            create_audit_log(
                db=db,
                action=AuditAction.VALIDATION_FAILED,
                description=f"Contract validation failed",
                user_id=user_uuid,
                resource_type="proposal",
                resource_id=proposal_uuid,
                error_message=str(e),
                success="failure"
            )
        except:
            pass
        
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def cleanup_old_files(days: int = 90):
    """
    Background task to clean up old processed files.
    
    Args:
        days: Delete files older than this many days
    """
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        from app.db.models.upload import Upload
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        old_uploads = db.query(Upload).filter(
            Upload.uploaded_at < cutoff,
            Upload.text_extraction_status == ExtractionStatus.COMPLETED
        ).all()
        
        deleted_count = 0
        for upload in old_uploads:
            from app.db.crud.upload import delete_upload
            if delete_upload(db, upload.id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old files")
        return {"success": True, "deleted": deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()
