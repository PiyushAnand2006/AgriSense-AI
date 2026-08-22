"""Notification creation helper."""

from sqlalchemy.orm import Session

from app.models.user import Notification


def notify(db: Session, user_id: str, type: str, title: str, message: str) -> Notification:
    notification = Notification(user_id=user_id, type=type, title=title, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
