"""Notification schemas."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class NotificationOut(CamelModel):
    id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime | None = None


class NotificationListOut(CamelModel):
    items: list[NotificationOut]
    unread_count: int


class NotificationReadResult(CamelModel):
    id: str
    is_read: bool = True


class ReadAllResult(CamelModel):
    updated: int = Field(description="Number of notifications marked as read")
