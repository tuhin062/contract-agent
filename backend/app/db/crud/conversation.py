"""
CRUD operations for conversations and messages.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime

from app.db.models.conversation import (
    Conversation, ConversationMessage, AIInteractionLog,
    ConversationStatus, MessageRole
)


# ============== Conversation CRUD ==============

def create_conversation(
    db: Session,
    user_id: UUID,
    title: Optional[str] = None,
    context_file_ids: Optional[List[UUID]] = None
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
        context_file_ids=context_file_ids or [],
        status=ConversationStatus.ACTIVE
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: UUID) -> Optional[Conversation]:
    """Get conversation by ID."""
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()


def get_user_conversations(
    db: Session,
    user_id: UUID,
    status: Optional[ConversationStatus] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Conversation]:
    """Get conversations for a user."""
    query = db.query(Conversation).filter(Conversation.user_id == user_id)
    
    if status:
        query = query.filter(Conversation.status == status)
    else:
        query = query.filter(Conversation.status != ConversationStatus.DELETED)
    
    return query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()


def update_conversation(
    db: Session,
    conversation_id: UUID,
    title: Optional[str] = None,
    status: Optional[ConversationStatus] = None,
    context_file_ids: Optional[List[UUID]] = None
) -> Optional[Conversation]:
    """Update conversation."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    
    if title is not None:
        conversation.title = title
    if status is not None:
        conversation.status = status
    if context_file_ids is not None:
        conversation.context_file_ids = context_file_ids
    
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: UUID) -> bool:
    """Soft delete conversation."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return False
    
    conversation.status = ConversationStatus.DELETED
    db.commit()
    return True


def update_conversation_stats(
    db: Session,
    conversation_id: UUID,
    tokens_used: int = 0,
    model_used: Optional[str] = None
) -> Optional[Conversation]:
    """Update conversation statistics after a message."""
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    
    conversation.total_messages += 1
    conversation.total_tokens_used += tokens_used
    conversation.last_message_at = datetime.utcnow()
    
    if model_used:
        conversation.model_used = model_used
    
    db.commit()
    db.refresh(conversation)
    return conversation


# ============== Message CRUD ==============

def create_message(
    db: Session,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    sources: Optional[List[dict]] = None,
    confidence: Optional[str] = None,
    retrieved_chunks: int = 0,
    follow_up_suggestions: Optional[List[str]] = None,
    extracted_clauses: Optional[List[dict]] = None,
    risk_highlights: Optional[List[dict]] = None,
    tokens_used: int = 0,
    model_used: Optional[str] = None
) -> ConversationMessage:
    """Create a new message in a conversation."""
    message = ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources or [],
        confidence=confidence,
        retrieved_chunks=retrieved_chunks,
        follow_up_suggestions=follow_up_suggestions or [],
        extracted_clauses=extracted_clauses or [],
        risk_highlights=risk_highlights or [],
        tokens_used=tokens_used,
        model_used=model_used
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update conversation stats
    update_conversation_stats(db, conversation_id, tokens_used, model_used)
    
    return message


def get_conversation_messages(
    db: Session,
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ConversationMessage]:
    """Get messages for a conversation."""
    return db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.created_at).offset(skip).limit(limit).all()


def get_recent_messages(
    db: Session,
    conversation_id: UUID,
    limit: int = 10
) -> List[ConversationMessage]:
    """Get most recent messages for context."""
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(desc(ConversationMessage.created_at)).limit(limit).all()
    
    return list(reversed(messages))  # Return in chronological order


def rate_message(
    db: Session,
    message_id: UUID,
    rating: int,
    feedback: Optional[str] = None
) -> Optional[ConversationMessage]:
    """Add user rating/feedback to a message."""
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == message_id
    ).first()
    
    if not message:
        return None
    
    message.user_rating = max(1, min(5, rating))  # Clamp to 1-5
    if feedback:
        message.user_feedback = feedback
    
    db.commit()
    db.refresh(message)
    return message


# ============== AI Interaction Log CRUD ==============

def log_ai_interaction(
    db: Session,
    user_id: UUID,
    interaction_type: str,
    model_used: str,
    input_summary: Optional[str] = None,
    output_summary: Optional[str] = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    conversation_id: Optional[UUID] = None,
    context_file_ids: Optional[List[UUID]] = None,
    retrieved_chunk_count: int = 0,
    confidence_level: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> AIInteractionLog:
    """Log an AI interaction for audit purposes."""
    log = AIInteractionLog(
        user_id=user_id,
        conversation_id=conversation_id,
        interaction_type=interaction_type,
        model_used=model_used,
        input_summary=input_summary[:500] if input_summary else None,
        output_summary=output_summary[:500] if output_summary else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        context_file_ids=context_file_ids or [],
        retrieved_chunk_count=retrieved_chunk_count,
        confidence_level=confidence_level,
        response_time_ms=response_time_ms,
        success=success,
        error_message=error_message
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_user_ai_logs(
    db: Session,
    user_id: UUID,
    interaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AIInteractionLog]:
    """Get AI interaction logs for a user."""
    query = db.query(AIInteractionLog).filter(AIInteractionLog.user_id == user_id)
    
    if interaction_type:
        query = query.filter(AIInteractionLog.interaction_type == interaction_type)
    if start_date:
        query = query.filter(AIInteractionLog.created_at >= start_date)
    if end_date:
        query = query.filter(AIInteractionLog.created_at <= end_date)
    
    return query.order_by(desc(AIInteractionLog.created_at)).offset(skip).limit(limit).all()


def get_ai_usage_stats(db: Session, user_id: UUID) -> dict:
    """Get AI usage statistics for a user."""
    from sqlalchemy import func
    
    logs = db.query(AIInteractionLog).filter(AIInteractionLog.user_id == user_id)
    
    total_interactions = logs.count()
    total_tokens = logs.with_entities(func.sum(AIInteractionLog.total_tokens)).scalar() or 0
    
    by_type = logs.with_entities(
        AIInteractionLog.interaction_type,
        func.count(AIInteractionLog.id)
    ).group_by(AIInteractionLog.interaction_type).all()
    
    return {
        "total_interactions": total_interactions,
        "total_tokens_used": total_tokens,
        "interactions_by_type": {t: c for t, c in by_type}
    }



