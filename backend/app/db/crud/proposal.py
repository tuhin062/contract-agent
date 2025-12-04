"""
CRUD operations for Proposal model.
Handles proposal creation, validation tracking, and risk assessment.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.models.proposal import Proposal, ValidationStatus, RiskLevel
from app.db.models.upload import Upload


def get_proposal(db: Session, proposal_id: UUID) -> Optional[Proposal]:
    """Get proposal by ID."""
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()


def get_proposals(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    created_by: Optional[UUID] = None,
    contract_id: Optional[UUID] = None,
    validation_status: Optional[ValidationStatus] = None,
    risk_level: Optional[RiskLevel] = None
) -> List[Proposal]:
    """
    Get list of proposals with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        created_by: Filter by creator
        contract_id: Filter by associated contract
        validation_status: Filter by validation status
        risk_level: Filter by risk level
    """
    query = db.query(Proposal)
    
    if created_by:
        query = query.filter(Proposal.created_by == created_by)
    if contract_id:
        query = query.filter(Proposal.contract_id == contract_id)
    if validation_status:
        query = query.filter(Proposal.validation_status == validation_status)
    if risk_level:
        query = query.filter(Proposal.risk_level == risk_level)
    
    return query.order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()


def get_proposals_count(
    db: Session,
    created_by: Optional[UUID] = None,
    validation_status: Optional[ValidationStatus] = None
) -> int:
    """Get total count of proposals with optional filters."""
    query = db.query(Proposal)
    
    if created_by:
        query = query.filter(Proposal.created_by == created_by)
    if validation_status:
        query = query.filter(Proposal.validation_status == validation_status)
    
    return query.count()


def create_proposal(
    db: Session,
    title: str,
    user_id: UUID,
    description: Optional[str] = None,
    contract_id: Optional[UUID] = None,
    upload_id: Optional[UUID] = None
) -> Proposal:
    """
    Create a new proposal.
    
    Args:
        db: Database session
        title: Proposal title
        user_id: Creator user ID
        description: Optional description
        contract_id: Optional associated contract ID
        upload_id: Optional associated upload ID
        
    Returns:
        Created proposal instance
    """
    db_proposal = Proposal(
        title=title,
        description=description,
        contract_id=contract_id,
        created_by=user_id,
        validation_status=ValidationStatus.PENDING
    )
    
    # Store upload reference in validation report if provided
    if upload_id:
        db_proposal.validation_report = {"upload_id": str(upload_id)}
    
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


def update_proposal_status(
    db: Session,
    proposal_id: UUID,
    status: ValidationStatus
) -> Optional[Proposal]:
    """Update proposal validation status."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        return None
    
    db_proposal.validation_status = status
    if status == ValidationStatus.COMPLETED:
        db_proposal.validated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


def update_proposal_validation(
    db: Session,
    proposal_id: UUID,
    risk_score: float,
    risk_level: RiskLevel,
    validation_report: dict,
    detected_clauses: List[dict] = None,
    compliance_checks: dict = None
) -> Optional[Proposal]:
    """
    Update proposal with validation results.
    
    Args:
        db: Database session
        proposal_id: Proposal ID
        risk_score: Calculated risk score (0.0 to 1.0)
        risk_level: Determined risk level
        validation_report: Full validation report
        detected_clauses: List of detected clauses
        compliance_checks: Compliance check results
    """
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        return None
    
    db_proposal.risk_score = risk_score
    db_proposal.risk_level = risk_level
    db_proposal.validation_report = validation_report
    db_proposal.detected_clauses = detected_clauses or []
    db_proposal.compliance_checks = compliance_checks or {}
    db_proposal.validation_status = ValidationStatus.COMPLETED
    db_proposal.validated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


def fail_proposal_validation(
    db: Session,
    proposal_id: UUID,
    error_message: str
) -> Optional[Proposal]:
    """Mark proposal validation as failed."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        return None
    
    db_proposal.validation_status = ValidationStatus.FAILED
    db_proposal.validation_report = {"error": error_message}
    
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


def delete_proposal(db: Session, proposal_id: UUID) -> bool:
    """Delete a proposal."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        return False
    
    db.delete(db_proposal)
    db.commit()
    return True


def get_proposals_by_risk_level(
    db: Session,
    risk_levels: List[RiskLevel],
    skip: int = 0,
    limit: int = 100
) -> List[Proposal]:
    """Get proposals filtered by multiple risk levels."""
    return db.query(Proposal).filter(
        Proposal.risk_level.in_(risk_levels)
    ).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()


def get_high_risk_proposals(db: Session, limit: int = 10) -> List[Proposal]:
    """Get proposals with high or critical risk levels."""
    return get_proposals_by_risk_level(
        db, 
        [RiskLevel.HIGH, RiskLevel.CRITICAL],
        limit=limit
    )
