"""
Admin settings and model configuration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.db.session import get_db
from app.db.crud.audit import create_audit_log
from app.db.models.user import User
from app.db.models.audit import AuditAction
from app.api.deps import require_admin
from app.core.config import settings

router = APIRouter()


class ModelConfig(BaseModel):
    """Model configuration schema."""
    chat_model: str = "openai/gpt-4o-mini"
    reasoning_model: str = "openai/gpt-4o"
    generation_model: str = "anthropic/claude-3.5-sonnet"
    embedding_model: str = "text-embedding-3-small"


class SystemSettings(BaseModel):
    """System settings schema."""
    file_max_size_mb: int = 100
    rate_limit_per_minute: int = 60
    rate_limit_llm_per_minute: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 100
    top_k_retrieval: int = 8
    min_similarity_score: float = 0.7


# In-memory settings cache (in production, use Redis or database)
_settings_cache: Dict[str, Any] = {}


@router.get("/models")
async def get_model_config(
    current_user: User = Depends(require_admin)
):
    """Get current model configuration."""
    return {
        "chat_model": _settings_cache.get("chat_model", settings.OPENROUTER_CHAT_MODEL),
        "reasoning_model": _settings_cache.get("reasoning_model", settings.OPENROUTER_REASONING_MODEL),
        "generation_model": _settings_cache.get("generation_model", settings.OPENROUTER_GENERATION_MODEL),
        "embedding_model": _settings_cache.get("embedding_model", settings.OPENROUTER_EMBEDDING_MODEL),
        "available_models": [
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "type": "chat", "cost": "low"},
            {"id": "openai/gpt-4o", "name": "GPT-4o", "type": "reasoning", "cost": "high"},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "type": "generation", "cost": "high"},
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "type": "chat", "cost": "low"},
            {"id": "google/gemini-pro", "name": "Gemini Pro", "type": "chat", "cost": "medium"},
            {"id": "meta-llama/llama-3.1-70b-instruct", "name": "Llama 3.1 70B", "type": "chat", "cost": "medium"},
        ]
    }


@router.put("/models")
async def update_model_config(
    config: ModelConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update model configuration (admin only)."""
    old_config = {
        "chat_model": _settings_cache.get("chat_model"),
        "reasoning_model": _settings_cache.get("reasoning_model"),
        "generation_model": _settings_cache.get("generation_model"),
        "embedding_model": _settings_cache.get("embedding_model")
    }
    
    _settings_cache["chat_model"] = config.chat_model
    _settings_cache["reasoning_model"] = config.reasoning_model
    _settings_cache["generation_model"] = config.generation_model
    _settings_cache["embedding_model"] = config.embedding_model
    
    # Audit log
    create_audit_log(
        db=db,
        action=AuditAction.SETTINGS_UPDATED,
        description="Model configuration updated",
        user_id=current_user.id,
        details={"old": old_config, "new": config.model_dump()}
    )
    
    return {"message": "Model configuration updated", "config": config}


@router.get("/system")
async def get_system_settings(
    current_user: User = Depends(require_admin)
):
    """Get system settings."""
    return {
        "file_max_size_mb": settings.FILE_MAX_SIZE / (1024 * 1024),
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        "rate_limit_llm_per_minute": settings.RATE_LIMIT_LLM_PER_MINUTE,
        "chunk_size": _settings_cache.get("chunk_size", 1000),
        "chunk_overlap": _settings_cache.get("chunk_overlap", 100),
        "top_k_retrieval": _settings_cache.get("top_k_retrieval", 8),
        "min_similarity_score": _settings_cache.get("min_similarity_score", 0.7),
        "pinecone_index": settings.PINECONE_INDEX_NAME,
        "pinecone_namespace": settings.PINECONE_NAMESPACE,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }


@router.put("/system")
async def update_system_settings(
    system_settings: SystemSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update system settings (admin only)."""
    _settings_cache["chunk_size"] = system_settings.chunk_size
    _settings_cache["chunk_overlap"] = system_settings.chunk_overlap
    _settings_cache["top_k_retrieval"] = system_settings.top_k_retrieval
    _settings_cache["min_similarity_score"] = system_settings.min_similarity_score
    
    # Audit log
    create_audit_log(
        db=db,
        action=AuditAction.SETTINGS_UPDATED,
        description="System settings updated",
        user_id=current_user.id,
        details=system_settings.model_dump()
    )
    
    return {"message": "System settings updated", "settings": system_settings}


@router.get("/health")
async def get_system_health(
    current_user: User = Depends(require_admin)
):
    """Get system health status."""
    from app.services.pinecone_client import pinecone_client
    
    # Check Pinecone
    pinecone_status = "connected" if pinecone_client.connect() else "disconnected"
    
    # Get Pinecone stats
    pinecone_stats = {}
    try:
        pinecone_stats = pinecone_client.get_index_stats()
    except:
        pass
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": "connected",
            "pinecone": pinecone_status,
            "openrouter": "configured"
        },
        "pinecone_stats": pinecone_stats
    }


@router.post("/cache/clear")
async def clear_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Clear settings cache."""
    _settings_cache.clear()
    
    # Audit log
    create_audit_log(
        db=db,
        action=AuditAction.SETTINGS_UPDATED,
        description="Settings cache cleared",
        user_id=current_user.id
    )
    
    return {"message": "Cache cleared"}

