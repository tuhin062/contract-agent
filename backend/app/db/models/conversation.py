"""
Conversation model for persisting AI chat sessions.
Tracks full conversation history with metadata and sources.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """Conversation model for AI chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(500), nullable=True)  # Auto-generated or user-set
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    
    # Context files used in this conversation
    context_file_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    
    # Conversation metadata
    total_messages = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationMessage.created_at")
    
    def __repr__(self):
        return f"<Conversation {self.id} - {self.title or 'Untitled'}>"


class ConversationMessage(Base):
    """Individual message within a conversation."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # For assistant messages - source citations
    sources = Column(JSONB, default=[])  # List of source citations
    confidence = Column(String(20), nullable=True)  # high/medium/low
    retrieved_chunks = Column(Integer, default=0)
    
    # Follow-up suggestions (for assistant messages)
    follow_up_suggestions = Column(ARRAY(String), default=[])
    
    # Extracted entities/clauses (for assistant messages)
    extracted_clauses = Column(JSONB, default=[])
    risk_highlights = Column(JSONB, default=[])
    
    # Token usage
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    
    # Feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 rating
    user_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} - {self.role.value}>"


class AIInteractionLog(Base):
    """Audit log for all AI interactions - for compliance and monitoring."""
    
    __tablename__ = "ai_interaction_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # chat, validation, generation, analysis
    model_used = Column(String(100), nullable=False)
    
    # Input/Output (hashed or truncated for privacy)
    input_summary = Column(Text, nullable=True)  # First 500 chars of input
    output_summary = Column(Text, nullable=True)  # First 500 chars of output
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Context
    context_file_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])
    retrieved_chunk_count = Column(Integer, default=0)
    
    # Quality metrics
    confidence_level = Column(String(20), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AIInteractionLog {self.id} - {self.interaction_type}>"



