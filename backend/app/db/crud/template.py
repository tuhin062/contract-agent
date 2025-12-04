"""
CRUD operations for Template model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
import re

from app.db.models.template import Template
from app.schemas.template import TemplateCreate, TemplateUpdate


def get_template(db: Session, template_id: UUID) -> Optional[Template]:
    """Get template by ID."""
    return db.query(Template).filter(Template.id == template_id).first()


def get_template_by_name(db: Session, name: str) -> Optional[Template]:
    """Get template by name."""
    return db.query(Template).filter(Template.name == name).first()


def get_templates(
    db: Session,
    category: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[Template]:
    """Get list of templates with optional filters."""
    query = db.query(Template)
    
    if category:
        query = query.filter(Template.category == category)
    if active_only:
        query = query.filter(Template.is_active == True)
    
    return query.order_by(Template.created_at.desc()).offset(skip).limit(limit).all()


def create_template(
    db: Session,
    template: TemplateCreate,
    user_id: UUID
) -> Template:
    """Create a new template."""
    # Convert placeholders to dict format for JSONB
    placeholders_dict = [p.model_dump() for p in template.placeholders]
    
    db_template = Template(
        name=template.name,
        description=template.description,
        content=template.content,
        category=template.category,
        placeholders=placeholders_dict,
        metadata=template.metadata,
        created_by=user_id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_template(
    db: Session,
    template_id: UUID,
    template_update: TemplateUpdate
) -> Optional[Template]:
    """Update template information."""
    db_template = get_template(db, template_id)
    if not db_template:
        return None
    
    update_data = template_update.model_dump(exclude_unset=True)
    
    # Handle placeholders separately
    if "placeholders" in update_data and update_data["placeholders"]:
        update_data["placeholders"] = [p.model_dump() for p in update_data["placeholders"]]
    
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


def delete_template(db: Session, template_id: UUID) -> bool:
    """Delete (deactivate) a template."""
    db_template = get_template(db, template_id)
    if not db_template:
        return False
    
    # Soft delete by marking inactive
    db_template.is_active = False
    db.commit()
    return True


def generate_contract_from_template(
    template: Template,
    values: dict
) -> str:
    """
    Replace placeholders in template with provided values.
    
    Args:
        template: Template object
        values: Dictionary of placeholder values {key: value}
        
    Returns:
        Processed contract content
    """
    content = template.content
    
    # Replace each placeholder
    for placeholder in template.placeholders:
        key = placeholder.get("key", "")
        value = values.get(key, placeholder.get("default", ""))
        
        # Replace placeholder in content
        content = content.replace(key, str(value))
    
    return content
