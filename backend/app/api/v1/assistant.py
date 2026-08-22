"""Farmer assistant endpoints (rule-based or external API, both backend-owned)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import AssistantConversation, AssistantMessage, User
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantConversationOut,
    AssistantMessageOut,
)
from app.services.assistant_service import chat as assistant_chat

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(
    payload: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_id, assistant_status, reply = await assistant_chat(
        db, current_user, payload.message.strip(), payload.conversation_id
    )
    return AssistantChatResponse(
        conversation_id=conversation_id,
        reply=AssistantMessageOut(
            id=reply.id, role=reply.role, content=reply.content, created_at=reply.created_at
        ),
        status=assistant_status,
    )


@router.get("/conversations", response_model=list[AssistantConversationOut])
def conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = list(
        db.scalars(
            select(AssistantConversation)
            .where(AssistantConversation.user_id == current_user.id)
            .order_by(AssistantConversation.created_at.desc())
            .limit(30)
        )
    )
    return [
        AssistantConversationOut(id=c.id, title=c.title, created_at=c.created_at, messages=[])
        for c in rows
    ]


@router.get("/conversations/{conversation_id}", response_model=AssistantConversationOut)
def conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.get(AssistantConversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    messages = list(
        db.scalars(
            select(AssistantMessage)
            .where(AssistantMessage.conversation_id == conversation.id)
            .order_by(AssistantMessage.id.asc())
        )
    )
    return AssistantConversationOut(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[
            AssistantMessageOut(id=m.id, role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ],
    )
