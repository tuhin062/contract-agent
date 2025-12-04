"""
Pydantic schemas for chat operations.
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== Message Schemas ==============

class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class SourceCitation(BaseModel):
    """Source citation from RAG retrieval."""
    text: str
    score: float = Field(..., ge=0, le=1)
    file_id: Optional[str] = None
    filename: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None


class ExtractedClause(BaseModel):
    """Extracted legal clause."""
    type: str
    text: str
    confidence: str = "medium"


class RiskHighlight(BaseModel):
    """Highlighted risk in document."""
    severity: str
    matched_text: str
    context: str
    recommendation: str


# ============== Request Schemas ==============

class ChatRequest(BaseModel):
    """Chat request with RAG context."""
    messages: List[ChatMessage]
    context_files: Optional[List[str]] = []
    conversation_id: Optional[str] = None
    top_k: Optional[int] = Field(8, ge=1, le=20)
    model: Optional[str] = None
    stream: bool = False


class ConversationCreate(BaseModel):
    """Create new conversation."""
    title: Optional[str] = None
    context_file_ids: Optional[List[UUID4]] = []


class MessageRating(BaseModel):
    """Rate a message."""
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


# ============== Response Schemas ==============

class ChatResponse(BaseModel):
    """Chat response with all metadata."""
    answer: str
    sources: List[SourceCitation] = []
    confidence: str = "medium"
    retrieved_chunks: int = 0
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    follow_up_suggestions: List[str] = []
    extracted_clauses: List[Dict[str, Any]] = []
    risk_highlights: List[Dict[str, Any]] = []
    conversation_id: Optional[str] = None
    response_time_ms: Optional[int] = None


class MessageResponse(BaseModel):
    """Conversation message response."""
    id: UUID4
    conversation_id: UUID4
    role: str
    content: str
    sources: List[Dict[str, Any]] = []
    confidence: Optional[str] = None
    retrieved_chunks: int = 0
    follow_up_suggestions: List[str] = []
    extracted_clauses: List[Dict[str, Any]] = []
    risk_highlights: List[Dict[str, Any]] = []
    tokens_used: int = 0
    model_used: Optional[str] = None
    user_rating: Optional[int] = None
    user_feedback: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Full conversation response."""
    id: UUID4
    title: Optional[str] = None
    user_id: UUID4
    status: str
    context_file_ids: List[UUID4] = []
    total_messages: int = 0
    total_tokens_used: int = 0
    model_used: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    messages: List[MessageResponse] = []
    
    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Conversation list item."""
    id: UUID4
    title: Optional[str] = None
    status: str
    total_messages: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class StreamEvent(BaseModel):
    """SSE stream event."""
    type: str  # 'sources', 'content', 'done', 'error'
    data: Any
