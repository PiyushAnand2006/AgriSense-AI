"""Startup index migrations reach both fresh and pre-existing databases.

The composite indexes cover the app's hottest read paths (health records list,
notifications list/unread count); market_prices is already covered by the
`uq_price_per_day` unique constraint, which Postgres implements as a btree
index on (crop_id, market_id, price_date).
"""

from sqlalchemy import inspect


def _index_names(inspector, table: str) -> set[str]:
    return {idx["name"] for idx in inspector.get_indexes(table)}


def test_composite_indexes_created_at_startup(client):
    from app.db.session import engine

    inspector = inspect(engine)

    health = _index_names(inspector, "health_records")
    assert "ix_health_records_user_crop_date" in health

    notifications = _index_names(inspector, "notifications")
    assert "ix_notifications_user_read_date" in notifications


def test_market_prices_unique_constraint_serves_price_queries(client):
    from app.db.session import engine

    inspector = inspect(engine)
    uniques = {uq["name"] for uq in inspector.get_unique_constraints("market_prices")}
    assert "uq_price_per_day" in uniques

    # Sanity: the constraint's column order matches the query shape
    # (crop_id, market_id prefix filter + price_date sort).
    constraint = next(uq for uq in inspector.get_unique_constraints("market_prices") if uq["name"] == "uq_price_per_day")
    assert tuple(constraint["column_names"]) == ("crop_id", "market_id", "price_date")


def test_index_migration_is_idempotent(client):
    # init_db has already run once via the app lifespan; running the
    # ensure pass again must not raise (checkfirst=True everywhere).
    from app.db.session import _ensure_indexes, engine

    _ensure_indexes()

    inspector = inspect(engine)
    assert "ix_health_records_user_crop_date" in _index_names(inspector, "health_records")
