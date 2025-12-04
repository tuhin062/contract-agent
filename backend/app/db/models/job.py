"""
Job database model for async task tracking.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    VALIDATION = "validation"
    FILE_PROCESSING = "file_processing"
    CONTRACT_GENERATION = "contract_generation"
    OTHER = "other"


class Job(Base):
    """Job model for tracking async background tasks."""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Job information
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    
    # Task details
    task_name = Column(String)  # Worker function name
    task_args = Column(JSONB, default={})  # Arguments for the task
    
    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100
    progress_message = Column(String)
    
    # Results
    result = Column(JSONB)  # Task result data
    error_message = Column(Text)
    
    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Job {self.job_type} ({self.status})>"
