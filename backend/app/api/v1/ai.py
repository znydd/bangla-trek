import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    AIConversationCreate,
    AIConversationDetailRead,
    AIConversationRead,
    AIMessageCreate,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/conversations", response_model=AIConversationRead)
async def create_conversation(
    req: AIConversationCreate = AIConversationCreate(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Create a new AI conversation."""
    ai_svc = AIService(db)
    return ai_svc.create_conversation(user_id=current_user.id, title=req.title)


@router.get("/conversations", response_model=List[AIConversationRead])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: List all AI conversations for the logged-in user."""
    ai_svc = AIService(db)
    return ai_svc.list_conversations(user_id=current_user.id)


@router.get("/conversations/{conversation_id}", response_model=AIConversationDetailRead)
async def get_conversation_detail(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Fetch conversation detail with messages and pinned context places."""
    ai_svc = AIService(db)
    return ai_svc.get_conversation_detail(
        conversation_id=conversation_id, user_id=current_user.id
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Delete an AI conversation."""
    ai_svc = AIService(db)
    ai_svc.delete_conversation(conversation_id=conversation_id, user_id=current_user.id)
    return {"message": "Conversation deleted successfully"}


@router.put("/conversations/{conversation_id}/places/{place_id}", response_model=AIConversationDetailRead)
async def add_place_to_conversation_context(
    conversation_id: uuid.UUID,
    place_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Pin an approved place to conversation context card."""
    ai_svc = AIService(db)
    return ai_svc.add_place_to_context(
        conversation_id=conversation_id,
        user_id=current_user.id,
        place_id=place_id,
    )


@router.delete("/conversations/{conversation_id}/places/{place_id}", response_model=AIConversationDetailRead)
async def remove_place_from_conversation_context(
    conversation_id: uuid.UUID,
    place_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Remove a place from conversation context card."""
    ai_svc = AIService(db)
    return ai_svc.remove_place_from_context(
        conversation_id=conversation_id,
        user_id=current_user.id,
        place_id=place_id,
    )


@router.post("/conversations/{conversation_id}/messages")
async def send_ai_message(
    conversation_id: uuid.UUID,
    req: AIMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Protected API: Send message to AI assistant and receive SSE event stream."""
    ai_svc = AIService(db)
    generator = ai_svc.stream_user_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        user_content=req.content,
    )
    return StreamingResponse(generator, media_type="text/event-stream")
