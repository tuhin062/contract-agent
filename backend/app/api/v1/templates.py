"""
Template endpoints for managing contract templates.
Handles create, read, update, and delete operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.crud.template import (
    get_template,
    get_template_by_name,
    get_templates,
    create_template,
    update_template,
    delete_template
)
from app.schemas.template import (
    Template as TemplateSchema,
    TemplateListItem,
    TemplateCreate,
    TemplateUpdate
)
from app.db.models.user import User
from app.api.deps import get_current_user, require_admin
from app.core.errors import NotFoundException, ConflictException, ForbiddenException

router = APIRouter()


@router.post("", response_model=TemplateSchema, status_code=status.HTTP_201_CREATED)
async def create_new_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Admin only
):
    """Create a new template (admin only)."""
    # Check if template with same name exists
    existing = get_template_by_name(db, template.name)
    if existing:
        raise ConflictException(detail="Template with this name already exists")
    
    db_template = create_template(db, template, current_user.id)
    return TemplateSchema.model_validate(db_template)


@router.get("", response_model=List[TemplateListItem])
async def list_templates(
    category: str = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all templates with optional filters."""
    templates = get_templates(db, category, active_only, skip, limit)
    return [TemplateListItem.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateSchema)
async def get_template_details(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get template details by ID."""
    db_template = get_template(db, template_id)
    if not db_template:
        raise NotFoundException(detail="Template not found")
    
    return TemplateSchema.model_validate(db_template)


@router.put("/{template_id}", response_model=TemplateSchema)
async def update_template_details(
    template_id: str,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Admin only
):
    """Update template details (admin only)."""
    updated_template = update_template(db, template_id, template_update)
    if not updated_template:
        raise NotFoundException(detail="Template not found")
    
    return TemplateSchema.model_validate(updated_template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template_endpoint(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Admin only
):
    """Delete (deactivate) a template (admin only)."""
    success = delete_template(db, template_id)
    if not success:
        raise NotFoundException(detail="Template not found")
    
    return None
