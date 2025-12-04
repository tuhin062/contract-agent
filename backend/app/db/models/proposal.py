"""
Proposal database model for tracking contract proposals and validations.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class ValidationStatus(str, enum.Enum):
    """Validation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Proposal(Base):
    """Proposal model for contract validation and review."""
    
    __tablename__ = "proposals"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Proposal information
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Associated contract (if validating existing contract)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True)
    
    # Validation status
    validation_status = Column(
        Enum(ValidationStatus),
        default=ValidationStatus.PENDING,
        nullable=False
    )
    
    # Risk assessment
    risk_level = Column(Enum(RiskLevel), nullable=True)
    risk_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Validation results
    validation_report = Column(JSONB, default={})
    # Structure: {
    #   "issues": [{"type": "...", "severity": "...", "message": "...", "location": "..."}],
    #   "suggestions": [...],
    #   "compliance": {...},
    #   "clauses": [...]
    # }
    
    # Analysis results
    detected_clauses = Column(JSONB, default=[])
    compliance_checks = Column(JSONB, default={})
    
    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    validated_at = Column(DateTime(timezone=True))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    contract = relationship("Contract", foreign_keys=[contract_id])
    
    def __repr__(self):
        return f"<Proposal {self.title} ({self.validation_status})>"
