"""AI assistant schemas."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class AssistantChatRequest(CamelModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None


class AssistantMessageOut(CamelModel):
    id: int | None = None
    role: str
    content: str
    created_at: datetime | None = None


class AssistantChatResponse(CamelModel):
    conversation_id: str
    reply: AssistantMessageOut
    status: str = "MOCK_ASSISTANT"


class AssistantConversationOut(CamelModel):
    id: str
    title: str
    created_at: datetime | None = None
    messages: list[AssistantMessageOut] = []
