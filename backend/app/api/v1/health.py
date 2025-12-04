"""
Health check and diagnostic endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.storage import storage
from app.services.pinecone_client import pinecone_client
from app.core.config import settings
from pathlib import Path
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "contract-agent-api"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system diagnostics."""
    checks = {
        "api": {"status": "ok", "message": "API is running"},
        "database": {"status": "unknown", "message": ""},
        "storage": {"status": "unknown", "message": ""},
        "pinecone": {"status": "unknown", "message": ""}
    }
    
    # Check database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        checks["database"] = {"status": "error", "message": f"Database error: {str(e)}"}
    
    # Check storage
    try:
        storage_path = Path(settings.FILE_STORAGE_PATH)
        if storage_path.exists() and storage_path.is_dir():
            # Test write
            test_file = storage_path / ".test_write"
            try:
                test_file.write_text("test")
                test_file.unlink()
                checks["storage"] = {"status": "ok", "message": f"Storage writable: {storage_path}"}
            except Exception as e:
                checks["storage"] = {"status": "error", "message": f"Storage not writable: {str(e)}"}
        else:
            checks["storage"] = {"status": "error", "message": f"Storage path does not exist: {storage_path}"}
    except Exception as e:
        checks["storage"] = {"status": "error", "message": f"Storage check failed: {str(e)}"}
    
    # Check Pinecone
    try:
        if pinecone_client.connect():
            stats = pinecone_client.get_index_stats()
            checks["pinecone"] = {"status": "ok", "message": f"Pinecone connected. Index stats: {stats}"}
        else:
            checks["pinecone"] = {"status": "error", "message": "Failed to connect to Pinecone"}
    except Exception as e:
        checks["pinecone"] = {"status": "error", "message": f"Pinecone error: {str(e)}"}
    
    # Overall status
    all_ok = all(check["status"] == "ok" for check in checks.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "config": {
            "file_storage_path": str(settings.FILE_STORAGE_PATH),
            "file_max_size_mb": settings.FILE_MAX_SIZE / (1024 * 1024),
            "allowed_extensions": [".pdf", ".docx", ".txt"]
        }
    }



