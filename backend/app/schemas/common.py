"""Shared schema primitives.

All fields use Python snake_case naming. The ``CamelModel`` base applies
a custom ``to_camel`` alias generator so JSON on the wire uses camelCase
(e.g. ``page_size`` -> ``pageSize``, ``trend7d`` -> ``trend7d``).

Routers construct responses with snake_case keyword arguments.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict


def _to_camel(name: str) -> str:
    """Convert snake_case to camelCase, preserving digits before letters lowercased.

    Standard ``to_camel`` would turn ``trend7d`` into ``trend7D``; this
    version keeps it as ``trend7d`` — the wire format the frontend expects.
    """
    parts = name.split("_")
    return parts[0] + "".join(part if part[0].isdigit() else part.capitalize() for part in parts[1:])


T = TypeVar("T")


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Always serialize using camelCase aliases."""
        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)


class Page(CamelModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
