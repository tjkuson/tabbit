"""Debate database schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Debate:
    """Schema for a debate with ID."""

    id: int
    round_id: int


@dataclass(frozen=True, slots=True)
class ListDebatesQuery:
    """Schema for listing debates with filters."""

    offset: int = 0
    limit: int = 100
    round_id: int | None = None
