"""
Validation endpoints for contract analysis and risk assessment.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.db.crud.contract import get_contract
from app.db.models.user import User
from app.db.models.proposal import Proposal, ValidationStatus, RiskLevel
from app.db.models.contract import Contract
from app.schemas.proposal import (
    ValidateContractRequest,
    ValidationReport,
    ValidationIssue,
    DetectedClause
)
from app.api.deps import get_current_user
from app.services.validation import validation_service
from app.core.errors import NotFoundException, ForbiddenException

router = APIRouter()


@router.post("/contracts/{contract_id}/validate", response_model=ValidationReport)
async def validate_contract(
    contract_id: str,
    request: ValidateContractRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a contract using LLM analysis.
    
    Analyzes the contract for:
    - Potential issues and risks
    - Missing or problematic clauses
    - Compliance checks
    - Improvement suggestions
    
    Returns a detailed validation report with risk score.
    """
    # Get contract
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to validate this contract")
    
    # Create proposal record if requested
    proposal = None
    if request.create_proposal:
        proposal = Proposal(
            title=f"Validation: {db_contract.title}",
            description=f"Automated validation of contract {db_contract.id}",
            contract_id=db_contract.id,
            validation_status=ValidationStatus.IN_PROGRESS,
            created_by=current_user.id
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
    
    try:
        # Run validation
        validation_result = await validation_service.validate_contract(
            contract_text=db_contract.content,
            contract_type=request.contract_type
        )
        
        # Update proposal if created
        if proposal:
            proposal.validation_status = ValidationStatus.COMPLETED
            proposal.risk_score = validation_result.get("risk_score", 0.5)
            proposal.risk_level = RiskLevel(validation_result.get("risk_level", "MEDIUM").upper())
            proposal.validation_report = validation_result
            proposal.detected_clauses = validation_result.get("clauses", [])
            proposal.compliance_checks = validation_result.get("compliance", {})
            proposal.validated_at = datetime.utcnow()
            db.commit()
        
        # Build response
        issues = [
            ValidationIssue(severity=issue["severity"], message=issue["message"])
            for issue in validation_result.get("issues", [])
        ]
        
        clauses = [
            DetectedClause(name=clause["name"], description=clause["description"])
            for clause in validation_result.get("clauses", [])
        ]
        
        return ValidationReport(
            proposal_id=proposal.id if proposal else None,
            risk_score=validation_result.get("risk_score", 0.5),
            risk_level=validation_result.get("risk_level", "MEDIUM"),
            issues=issues,
            suggestions=validation_result.get("suggestions", []),
            clauses=clauses,
            compliance=validation_result.get("compliance", {}),
            raw_analysis=validation_result.get("raw_analysis")
        )
        
    except Exception as e:
        # Update proposal status if created
        if proposal:
            proposal.validation_status = ValidationStatus.FAILED
            proposal.validation_report = {"error": str(e)}
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
