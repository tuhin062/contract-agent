"""
Contract endpoints for contract lifecycle management.
Handles create, read, update, approval workflow, and versioning.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.crud.contract import (
    get_contract,
    get_contracts,
    create_contract,
    update_contract,
    create_new_version,
    submit_for_review,
    approve_contract,
    reject_contract,
    execute_contract,
    archive_contract
)
from app.db.crud.template import get_template, generate_contract_from_template
from app.schemas.contract import (
    Contract as ContractSchema,
    ContractListItem,
    ContractCreate,
    ContractUpdate,
    ContractReview,
    ContractRejection,
    ContractFilters
)
from app.schemas.template import GenerateFromTemplate
from app.db.models.user import User
from app.db.models.contract import ContractStatus
from app.api.deps import get_current_user, require_reviewer
from app.core.errors import NotFoundException, BadRequestException, ForbiddenException

router = APIRouter()


@router.post("", response_model=ContractSchema, status_code=status.HTTP_201_CREATED)
async def create_new_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contract."""
    db_contract = create_contract(db, contract, current_user.id)
    return ContractSchema.model_validate(db_contract)


@router.post("/from-template", response_model=ContractSchema, status_code=status.HTTP_201_CREATED)
async def generate_contract(
    request: GenerateFromTemplate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a contract from a template."""
    # Get template
    template = get_template(db, request.template_id)
    if not template:
        raise NotFoundException(detail="Template not found")
    
    if not template.is_active:
        raise BadRequestException(detail="Template is inactive")
    
    # Generate content from template
    content = generate_contract_from_template(template, request.values)
    
    # Create contract
    contract_data = ContractCreate(
        title=request.title,
        description=request.description,
        content=content,
        template_id=template.id,
        metadata=request.metadata
    )
    
    db_contract = create_contract(db, contract_data, current_user.id)
    return ContractSchema.model_validate(db_contract)


@router.get("", response_model=List[ContractListItem])
async def list_contracts(
    status: ContractStatus = None,
    template_id: str = None,
    latest_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """    List contracts with optional filters."""
    filters = ContractFilters(
        status=status,
        created_by=current_user.id,  # Users see their own contracts
        template_id=template_id,
        latest_only=latest_only,
        skip=skip,
        limit=limit
    )
    
    contracts = get_contracts(db, filters)
    return [ContractListItem.model_validate(c) for c in contracts]


@router.get("/{contract_id}", response_model=ContractSchema)
async def get_contract_details(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contract details by ID."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to access this contract")
    
    return ContractSchema.model_validate(db_contract)


@router.put("/{contract_id}", response_model=ContractSchema)
async def update_contract_details(
    contract_id: str,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update contract details (draft only)."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to modify this contract")
    
    updated_contract = update_contract(db, contract_id, contract_update)
    return ContractSchema.model_validate(updated_contract)


@router.post("/{contract_id}/new-version", response_model=ContractSchema)
async def create_contract_version(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of an existing contract."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to version this contract")
    
    new_version = create_new_version(db, contract_id, current_user.id)
    return ContractSchema.model_validate(new_version)


@router.post("/{contract_id}/submit", response_model=ContractSchema)
async def submit_contract_for_review(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit contract for review."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to submit this contract")
    
    submitted_contract = submit_for_review(db, contract_id)
    return ContractSchema.model_validate(submitted_contract)


@router.post("/{contract_id}/approve", response_model=ContractSchema)
async def approve_contract_endpoint(
    contract_id: str,
    review: ContractReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer)  # Requires reviewer/admin role
):
    """Approve a contract (reviewer/admin only)."""
    approved_contract = approve_contract(db, contract_id, current_user.id, review.notes)
    if not approved_contract:
        raise NotFoundException(detail="Contract not found")
    
    return ContractSchema.model_validate(approved_contract)


@router.post("/{contract_id}/reject", response_model=ContractSchema)
async def reject_contract_endpoint(
    contract_id: str,
    rejection: ContractRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_reviewer)  # Requires reviewer/admin role
):
    """Reject a contract (reviewer/admin only)."""
    rejected_contract = reject_contract(db, contract_id, current_user.id, rejection.reason)
    if not rejected_contract:
        raise NotFoundException(detail="Contract not found")
    
    return ContractSchema.model_validate(rejected_contract)


@router.post("/{contract_id}/execute", response_model=ContractSchema)
async def execute_contract_endpoint(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark contract as executed."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to execute this contract")
    
    executed_contract = execute_contract(db, contract_id)
    return ContractSchema.model_validate(executed_contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_contract_endpoint(
    contract_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive a contract."""
    db_contract = get_contract(db, contract_id)
    if not db_contract:
        raise NotFoundException(detail="Contract not found")
    
    # Verify ownership
    if db_contract.created_by != current_user.id:
        raise ForbiddenException(detail="Not authorized to archive this contract")
    
    archive_contract(db, contract_id)
    return None
