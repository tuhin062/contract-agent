"""
CRUD operations for Contract model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.models.contract import Contract, ContractStatus
from app.schemas.contract import ContractCreate, ContractUpdate, ContractFilters
from app.core.errors import NotFoundException, BadRequestException


def get_contract(db: Session, contract_id: UUID) -> Optional[Contract]:
    """Get contract by ID."""
    return db.query(Contract).filter(Contract.id == contract_id).first()


def get_contracts(
    db: Session,
    filters: ContractFilters
) -> List[Contract]:
    """
    Get list of contracts with filters.
    """
    query = db.query(Contract)
    
    if filters.status:
        query = query.filter(Contract.status == filters.status)
    if filters.created_by:
        query = query.filter(Contract.created_by == filters.created_by)
    if filters.template_id:
        query = query.filter(Contract.template_id == filters.template_id)
    if filters.latest_only:
        query = query.filter(Contract.is_latest_version == True)
    
    return query.order_by(Contract.created_at.desc()).offset(filters.skip).limit(filters.limit).all()


def create_contract(
    db: Session,
    contract: ContractCreate,
    user_id: UUID
) -> Contract:
    """Create a new contract."""
    db_contract = Contract(
        title=contract.title,
        description=contract.description,
        content=contract.content,
        template_id=contract.template_id,
        metadata=contract.metadata,
        created_by=user_id,
        status=ContractStatus.DRAFT
    )
    
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


def update_contract(
    db: Session,
    contract_id: UUID,
    contract_update: ContractUpdate
) -> Optional[Contract]:
    """Update contract information."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    # Can only update draft contracts
    if db_contract.status != ContractStatus.DRAFT:
        raise BadRequestException(detail="Can only update draft contracts")
    
    update_data = contract_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contract, field, value)
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


def create_new_version(
    db: Session,
    contract_id: UUID,
    user_id: UUID
) -> Contract:
    """Create a new version of an existing contract."""
    original = get_contract(db, contract_id)
    if not original:
        raise NotFoundException(detail="Original contract not found")
    
    # Mark original as not latest
    original.is_latest_version = False
    
    # Create new version
    new_contract = Contract(
        title=original.title,
        description=original.description,
        content=original.content,
        template_id=original.template_id,
        metadata=original.metadata.copy() if original.metadata else {},
        created_by=user_id,
        status=ContractStatus.DRAFT,
        version=original.version + 1,
        parent_contract_id=original.id,
        is_latest_version=True
    )
    
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract


def submit_for_review(
    db: Session,
    contract_id: UUID
) -> Optional[Contract]:
    """Submit contract for review."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    if db_contract.status != ContractStatus.DRAFT:
        raise BadRequestException(detail="Can only submit draft contracts")
    
    db_contract.status = ContractStatus.PENDING_REVIEW
    db_contract.submitted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


def approve_contract(
    db: Session,
    contract_id: UUID,
    reviewer_id: UUID,
    notes: Optional[str] = None
) -> Optional[Contract]:
    """Approve a contract."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    if db_contract.status != ContractStatus.PENDING_REVIEW:
        raise BadRequestException(detail="Can only approve contracts pending review")
    
    db_contract.status = ContractStatus.APPROVED
    db_contract.reviewed_by = reviewer_id
    db_contract.approved_by = reviewer_id
    db_contract.reviewed_at = datetime.utcnow()
    db_contract.review_notes = notes
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


def reject_contract(
    db: Session,
    contract_id: UUID,
    reviewer_id: UUID,
    reason: str
) -> Optional[Contract]:
    """Reject a contract."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    if db_contract.status != ContractStatus.PENDING_REVIEW:
        raise BadRequestException(detail="Can only reject contracts pending review")
    
    db_contract.status = ContractStatus.REJECTED
    db_contract.reviewed_by = reviewer_id
    db_contract.reviewed_at = datetime.utcnow()
    db_contract.rejection_reason = reason
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


def execute_contract(
    db: Session,
    contract_id: UUID
) -> Optional[Contract]:
    """Mark contract as executed."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return None
    
    if db_contract.status != ContractStatus.APPROVED:
        raise BadRequestException(detail="Can only execute approved contracts")
    
    db_contract.status = ContractStatus.EXECUTED
    db_contract.executed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


def archive_contract(
    db: Session,
    contract_id: UUID
) -> bool:
    """Archive a contract."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        return False
    
    db_contract.status = ContractStatus.ARCHIVED
    db.commit()
    return True
