"""
Configuration settings for the Contract Agent backend.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Contract Agent API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str  
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str  # Must be exactly 32 bytes for AES-256
    
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenRouter - Optimized for Legal Industry (No Hallucinations)
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Embedding Model - Must match Pinecone index dimension (1536)
    # Using text-embedding-3-small which produces 1536 dimensions
    OPENROUTER_EMBEDDING_MODEL: str = "openai/text-embedding-3-small"  # 1536 dimensions
    
    # Primary Chat Model - Claude 3.5 Sonnet: Best balance of speed, accuracy, and grounding
    # Excellent for RAG with strong instruction following and factual responses
    OPENROUTER_CHAT_MODEL: str = "anthropic/claude-3.5-sonnet"
    
    # Fallback Chat Model - Claude 3 Haiku: Fast, reliable fallback
    OPENROUTER_CHAT_MODEL_FALLBACK: str = "anthropic/claude-3-haiku"
    
    # Primary Reasoning Model - Claude 3 Opus: Most accurate for complex legal analysis
    # Superior for contract validation, risk assessment, and nuanced legal interpretation
    OPENROUTER_REASONING_MODEL: str = "anthropic/claude-3-opus-20240229"
    
    # Fallback Reasoning Model - Claude 3.5 Sonnet as fallback
    OPENROUTER_REASONING_MODEL_FALLBACK: str = "anthropic/claude-3.5-sonnet"
    
    # Generation Model - For contract drafting from templates
    OPENROUTER_GENERATION_MODEL: str = "anthropic/claude-3.5-sonnet"
    
    # Model temperature settings (lower = more deterministic/factual)
    LLM_TEMPERATURE_CHAT: float = 0.1  # Very low for factual RAG responses
    LLM_TEMPERATURE_REASONING: float = 0.0  # Zero for maximum accuracy in legal analysis
    LLM_TEMPERATURE_GENERATION: float = 0.3  # Slightly higher for creative drafting
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "contract-agent"
    PINECONE_NAMESPACE: str = ""  # Use default namespace where vectors exist
    
    # File Storage
    FILE_STORAGE_PATH: str = "./data/uploads"
    FILE_MAX_SIZE: int = 104857600  # 100MB
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000"
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_LLM_PER_MINUTE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Allow extra env variables without errors
    }


# Create global settings instance
settings = Settings()
