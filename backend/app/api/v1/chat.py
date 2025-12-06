"""
Enhanced Chat endpoints for RAG-powered question answering.
Features: Streaming SSE, conversation persistence, follow-ups, audit logging.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
import json
import time

from app.db.session import get_db
from app.db.crud.upload import get_upload
from app.db.crud.conversation import (
    create_conversation, get_conversation, get_user_conversations,
    update_conversation, delete_conversation,
    create_message, get_conversation_messages, get_recent_messages,
    rate_message, log_ai_interaction
)
from app.db.models.conversation import ConversationStatus, MessageRole
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatMessage, SourceCitation,
    ConversationCreate, ConversationResponse, ConversationListResponse,
    MessageResponse, MessageRating, StreamEvent
)
from app.db.models.user import User
from app.api.deps import get_current_user
from app.services.rag import rag_service  # Keep for backward compatibility
from app.services.rag_enhanced import enhanced_rag_service
from app.core.errors import BadRequestException, NotFoundException, ForbiddenException

router = APIRouter()
logger = logging.getLogger(__name__)


# ============== Conversation Management ==============

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation session."""
    # Validate file access if provided
    if request.context_file_ids:
        for file_id in request.context_file_ids:
            upload = get_upload(db, file_id)
            if not upload:
                raise NotFoundException(detail=f"File {file_id} not found")
            if upload.uploaded_by != current_user.id:
                raise ForbiddenException(detail=f"Not authorized to access file {file_id}")
    
    conversation = create_conversation(
        db=db,
        user_id=current_user.id,
        title=request.title,
        context_file_ids=request.context_file_ids
    )
    
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations", response_model=List[ConversationListResponse])
async def list_conversations(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's conversations."""
    conv_status = None
    if status_filter:
        try:
            # Convert to lowercase to match enum database values
            status_lower = status_filter.lower()
            # Map to enum - enum values are uppercase but DB stores lowercase
            if status_lower == "active":
                conv_status = ConversationStatus.ACTIVE
            elif status_lower == "archived":
                conv_status = ConversationStatus.ARCHIVED
            elif status_lower == "deleted":
                conv_status = ConversationStatus.DELETED
        except (ValueError, AttributeError):
            pass
    
    conversations = get_user_conversations(
        db=db,
        user_id=current_user.id,
        status=conv_status,
        skip=skip,
        limit=limit
    )
    
    return [ConversationListResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_detail(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation details with messages."""
    conversation = get_conversation(db, conversation_id)
    
    if not conversation:
        raise NotFoundException(detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise ForbiddenException(detail="Not authorized to access this conversation")
    
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for a conversation."""
    conversation = get_conversation(db, conversation_id)
    
    if not conversation:
        raise NotFoundException(detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise ForbiddenException(detail="Not authorized to access this conversation")
    
    messages = get_conversation_messages(db, conversation_id, skip, limit)
    return [MessageResponse.model_validate(m) for m in messages]


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_endpoint(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete (archive) a conversation."""
    conversation = get_conversation(db, conversation_id)
    
    if not conversation:
        raise NotFoundException(detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise ForbiddenException(detail="Not authorized to delete this conversation")
    
    delete_conversation(db, conversation_id)
    return None


@router.post("/messages/{message_id}/rate", response_model=MessageResponse)
async def rate_message_endpoint(
    message_id: UUID,
    rating: MessageRating,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rate a message (1-5 stars with optional feedback)."""
    message = rate_message(db, message_id, rating.rating, rating.feedback)
    
    if not message:
        raise NotFoundException(detail="Message not found")
    
    return MessageResponse.model_validate(message)


# ============== RAG Chat ==============

@router.post("/rag", response_model=ChatResponse)
async def chat_with_rag(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with RAG (Retrieval-Augmented Generation).
    Non-streaming endpoint for standard responses.
    """
    start_time = time.time()
    
    # Validate file access
    if request.context_files:
        for file_id in request.context_files:
            upload = get_upload(db, file_id)
            if not upload:
                raise BadRequestException(detail=f"File {file_id} not found")
            if upload.uploaded_by != current_user.id:
                raise ForbiddenException(detail=f"Not authorized to access file {file_id}")
    
    # Extract query from messages
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise BadRequestException(detail="No user message found")
    
    query = user_messages[-1].content
    
    # Build chat history
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages[:-1]
    ]
    
    # Handle conversation persistence
    conversation = None
    if request.conversation_id:
        conversation = get_conversation(db, request.conversation_id)
        if conversation and conversation.user_id != current_user.id:
            raise ForbiddenException(detail="Not authorized")
    
    try:
        # Call enhanced RAG service with advanced features
        result = await enhanced_rag_service.chat(
            query=query,
            file_ids=request.context_files if request.context_files else None,
            chat_history=chat_history if chat_history else None,
            top_k=request.top_k or 10,
            stream=False,
            include_follow_ups=True,
            include_clause_analysis=True
        )
        
        # Save messages to conversation if exists
        if conversation:
            # Save user message
            create_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=query
            )
            
            # Save assistant message
            create_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=result["answer"],
                sources=result.get("sources", []),
                confidence=result.get("confidence"),
                retrieved_chunks=result.get("retrieved_chunks", 0),
                follow_up_suggestions=result.get("follow_up_suggestions", []),
                extracted_clauses=result.get("extracted_clauses", []),
                risk_highlights=result.get("risk_highlights", []),
                tokens_used=result.get("tokens_used", 0),
                model_used=result.get("model_used")
            )
        
        # Log AI interaction for audit
        response_time_ms = int((time.time() - start_time) * 1000)
        log_ai_interaction(
            db=db,
            user_id=current_user.id,
            interaction_type="chat",
            model_used=result.get("model_used", "unknown"),
            input_summary=query,
            output_summary=result.get("answer", "")[:500],
            input_tokens=0,  # Would need to calculate
            output_tokens=result.get("tokens_used", 0),
            conversation_id=conversation.id if conversation else None,
            context_file_ids=request.context_files,
            retrieved_chunk_count=result.get("retrieved_chunks", 0),
            confidence_level=result.get("confidence"),
            response_time_ms=response_time_ms,
            success=True
        )
        
        # Convert sources to Pydantic models
        sources = [
            SourceCitation(
                text=src.get("text", "")[:300],
                score=src.get("score", 0),
                file_id=src.get("file_id"),
                filename=src.get("filename"),
                page=src.get("page"),
                chunk_index=src.get("chunk_index")
            )
            for src in result.get("sources", [])
        ]
        
        return ChatResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result.get("confidence", "low"),
            retrieved_chunks=result.get("retrieved_chunks", 0),
            model_used=result.get("model_used"),
            tokens_used=result.get("tokens_used"),
            follow_up_suggestions=result.get("follow_up_suggestions", []),
            extracted_clauses=result.get("extracted_clauses", []),
            risk_highlights=result.get("risk_highlights", []),
            conversation_id=str(conversation.id) if conversation else request.conversation_id,
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        logger.error(f"RAG chat error: {str(e)}")
        
        # Log failed interaction
        log_ai_interaction(
            db=db,
            user_id=current_user.id,
            interaction_type="chat",
            model_used="unknown",
            input_summary=query,
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/rag/stream")
async def chat_with_rag_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with RAG using Server-Sent Events for streaming responses.
    Returns real-time token-by-token response.
    """
    # Validate file access
    if request.context_files:
        for file_id in request.context_files:
            upload = get_upload(db, file_id)
            if not upload:
                raise BadRequestException(detail=f"File {file_id} not found")
            if upload.uploaded_by != current_user.id:
                raise ForbiddenException(detail=f"Not authorized to access file {file_id}")
    
    # Extract query
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise BadRequestException(detail="No user message found")
    
    query = user_messages[-1].content
    
    # Build chat history
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages[:-1]
    ]
    
    async def generate_stream():
        """Generate SSE stream."""
        start_time = time.time()
        full_response = ""
        
        try:
            # First, retrieve context using enhanced retrieval
            # Use lower min_score (0.15) for better retrieval, with adaptive fallback in service
            context_chunks = await enhanced_rag_service.retrieve_context_enhanced(
                query=query,
                file_ids=request.context_files if request.context_files else None,
                top_k=request.top_k or 10,
                min_score=0.15,  # Very low threshold - adaptive fallback will handle quality
                use_hybrid=True,
                enforce_diversity=True
            )
            
            # Send context info
            sources_data = [
                {
                    "text": src.get("text", "")[:200],
                    "score": src.get("score", 0),
                    "file_id": src.get("file_id"),
                    "page": src.get("page")
                }
                for src in context_chunks[:5]
            ]
            
            yield f"data: {json.dumps({'type': 'sources', 'data': sources_data})}\n\n"
            
            if not context_chunks:
                no_context_msg = "I don't have relevant information in the uploaded documents to answer this question."
                yield f"data: {json.dumps({'type': 'content', 'data': no_context_msg})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'data': {'confidence': 'low', 'retrieved_chunks': 0}})}\n\n"
                return
            
            # Generate answer using enhanced service
            result = await enhanced_rag_service.generate_grounded_answer(
                query=query,
                context_chunks=context_chunks,
                chat_history=chat_history
            )
            
            # Stream the answer word by word for SSE compatibility
            answer = result.get("answer", "")
            words = answer.split()
            for i, word in enumerate(words):
                word_with_space = word + (' ' if i < len(words) - 1 else '')
                full_response += word_with_space
                yield f"data: {json.dumps({'type': 'content', 'data': word_with_space})}\n\n"
            
            # Calculate metrics
            response_time_ms = int((time.time() - start_time) * 1000)
            confidence = result.get("confidence", "low")
            
            # Generate follow-ups asynchronously
            try:
                context_summary = " ".join(c["text"][:100] for c in context_chunks[:3])
                follow_ups = await rag_service.generate_follow_up_suggestions(
                    query, full_response[:500], context_summary
                )
            except:
                follow_ups = []
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'data': {'confidence': confidence, 'retrieved_chunks': len(context_chunks), 'response_time_ms': response_time_ms, 'follow_up_suggestions': follow_ups}})}\n\n"
            
            # Log interaction
            log_ai_interaction(
                db=db,
                user_id=current_user.id,
                interaction_type="chat_stream",
                model_used="claude-3.5-sonnet",
                input_summary=query,
                output_summary=full_response[:500],
                retrieved_chunk_count=len(context_chunks),
                confidence_level=confidence,
                response_time_ms=response_time_ms,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    pinecone_connected = rag_service.pinecone.connect()
    
    return {
        "status": "healthy" if pinecone_connected else "degraded",
        "pinecone": "connected" if pinecone_connected else "disconnected",
        "llm": "configured",
        "embeddings": "configured",
        "models": {
            "chat": "anthropic/claude-3.5-sonnet",
            "reasoning": "anthropic/claude-3-opus",
            "embeddings": "openai/text-embedding-3-large"
        }
    }
