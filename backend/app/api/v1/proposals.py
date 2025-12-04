"""
Proposal endpoints for validation tracking and management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.db.crud.proposal import (
    get_proposal,
    get_proposals,
    create_proposal,
    update_proposal_status,
    delete_proposal,
    get_high_risk_proposals,
    get_proposals_count
)
from app.db.models.user import User
from app.db.models.proposal import ValidationStatus, RiskLevel
from app.schemas.proposal import (
    Proposal as ProposalSchema,
    ProposalCreate,
    ProposalListItem,
    ProposalStats
)
from app.api.deps import get_current_user, require_reviewer
from app.core.errors import NotFoundException, ForbiddenException

router = APIRouter()


@router.post("", response_model=ProposalSchema, status_code=status.HTTP_201_CREATED)
async def create_new_proposal(
    proposal_data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new proposal for validation."""
    db_proposal = create_proposal(
        db=db,
        title=proposal_data.title,
        user_id=current_user.id,
        description=proposal_data.description,
        contract_id=proposal_data.contract_id,
        upload_id=proposal_data.upload_id
    )
    return ProposalSchema.model_validate(db_proposal)


@router.get("", response_model=List[ProposalListItem])
async def list_proposals(
    validation_status: Optional[ValidationStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List proposals with optional filters."""
    proposals = get_proposals(
        db=db,
        skip=skip,
        limit=limit,
        created_by=current_user.id,
        validation_status=validation_status,
        risk_level=risk_level
    )
    return [ProposalListItem.model_validate(p) for p in proposals]


@router.get("/stats", response_model=ProposalStats)
async def get_proposal_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal statistics for dashboard."""
    total = get_proposals_count(db, created_by=current_user.id)
    pending = get_proposals_count(
        db, 
        created_by=current_user.id, 
        validation_status=ValidationStatus.PENDING
    )
    completed = get_proposals_count(
        db, 
        created_by=current_user.id, 
        validation_status=ValidationStatus.COMPLETED
    )
    failed = get_proposals_count(
        db, 
        created_by=current_user.id, 
        validation_status=ValidationStatus.FAILED
    )
    
    return ProposalStats(
        total=total,
        pending=pending,
        completed=completed,
        failed=failed,
        in_progress=total - pending - completed - failed
    )


@router.get("/high-risk", response_model=List[ProposalListItem])
async def list_high_risk_proposals(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer)
):
    """Get high-risk proposals (reviewer/admin only)."""
    proposals = get_high_risk_proposals(db, limit=limit)
    return [ProposalListItem.model_validate(p) for p in proposals]


@router.get("/{proposal_id}", response_model=ProposalSchema)
async def get_proposal_details(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal details by ID."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        raise NotFoundException(detail="Proposal not found")
    
    # Check ownership
    if db_proposal.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to access this proposal")
    
    return ProposalSchema.model_validate(db_proposal)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal_endpoint(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a proposal."""
    db_proposal = get_proposal(db, proposal_id)
    if not db_proposal:
        raise NotFoundException(detail="Proposal not found")
    
    # Check ownership
    if db_proposal.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to delete this proposal")
    
    delete_proposal(db, proposal_id)
    return None
