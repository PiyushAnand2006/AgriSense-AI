"""Engine / session factory and startup helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base


def _build_engine():
    settings = get_settings()
    if settings.is_sqlite:
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables and seed reference data (idempotent)."""
    # Import models so they are registered on the Base metadata.
    import app.models  # noqa: F401
    from app.db.seed import seed

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
