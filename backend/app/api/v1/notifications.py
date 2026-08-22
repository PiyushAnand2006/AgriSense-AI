"""Notification endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import Notification, User
from app.schemas.notification import (
    NotificationListOut,
    NotificationOut,
    NotificationReadResult,
    ReadAllResult,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListOut)
def list_notifications(
    unreadOnly: bool = False,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(min(limit, 100))
    )
    if unreadOnly:
        stmt = stmt.where(Notification.is_read.is_(False))
    items = [NotificationOut.model_validate(n) for n in db.scalars(stmt)]
    unread_count = (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        )
        or 0
    )
    return NotificationListOut(items=items, unread_count=unread_count)


@router.patch("/read-all", response_model=ReadAllResult)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
    return ReadAllResult(updated=result.rowcount)


@router.patch("/{notification_id}/read", response_model=NotificationReadResult)
def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    notification.is_read = True
    db.commit()
    return NotificationReadResult(id=notification.id, is_read=True)
