"""
Proposal Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.db.models.proposal import ValidationStatus, RiskLevel


class ProposalBase(BaseModel):
    """Base proposal schema."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None


class ProposalCreate(ProposalBase):
    """Schema for creating a new proposal."""
    contract_id: Optional[UUID4] = None
    upload_id: Optional[UUID4] = None


class Proposal(ProposalBase):
    """Schema for proposal response."""
    model_config = {"from_attributes": True}
    
    id: UUID4
    contract_id: Optional[UUID4] = None
    validation_status: ValidationStatus
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[float] = None
    validation_report: Dict[str, Any] = {}
    detected_clauses: List[Dict[str, Any]] = []
    compliance_checks: Dict[str, Any] = {}
    created_by: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None


class ProposalListItem(BaseModel):
    """Schema for proposal list item."""
    model_config = {"from_attributes": True}
    
    id: UUID4
    title: str
    validation_status: ValidationStatus
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[float] = None
    created_by: UUID4
    created_at: datetime
    validated_at: Optional[datetime] = None


class ProposalStats(BaseModel):
    """Schema for proposal statistics."""
    total: int
    pending: int
    in_progress: int
    completed: int
    failed: int


class ValidateContractRequest(BaseModel):
    """Schema for contract validation request."""
    contract_type: Optional[str] = None
    create_proposal: bool = True
    custom_checks: List[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    """Schema for validation issue."""
    severity: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


class DetectedClause(BaseModel):
    """Schema for detected clause."""
    name: str
    description: str
    location: Optional[str] = None
    risk_level: Optional[str] = None


class ValidationReport(BaseModel):
    """Schema for validation report response."""
    proposal_id: Optional[UUID4] = None
    risk_score: float
    risk_level: str
    issues: List[ValidationIssue] = []
    suggestions: List[str] = []
    clauses: List[DetectedClause] = []
    compliance: Dict[str, Any] = {}
    raw_analysis: Optional[str] = None
