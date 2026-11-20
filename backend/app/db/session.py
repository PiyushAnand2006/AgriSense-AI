"""Engine / session factory and startup helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.base import Base


def _build_engine():
    settings = get_settings()
    db_url = settings.database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    if settings.is_sqlite:
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    return create_engine(db_url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_indexes() -> None:
    """Re-create any metadata indexes missing on the current database.

    create_all() never alters tables that already exist, so indexes added to
    the models after first launch would never reach a database initialised
    earlier (e.g. the production Supabase Postgres). checkfirst=True keeps
    this idempotent on every boot.
    """
    for table in Base.metadata.sorted_tables:
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)


def init_db() -> None:
    """Create tables and seed reference data (idempotent)."""
    # Import models so they are registered on the Base metadata.
    import app.models  # noqa: F401
    from app.db.seed import seed

    Base.metadata.create_all(bind=engine)
    _ensure_indexes()
    with SessionLocal() as db:
        seed(db)
