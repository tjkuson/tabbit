"""Judge database schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JudgeCreate:
    """Schema for creating a judge."""

    tournament_id: int
    name: str


@dataclass(frozen=True, slots=True)
class Judge:
    """Schema for a judge with ID."""

    id: int
    tournament_id: int
    name: str


@dataclass(frozen=True, slots=True)
class ListJudgesQuery:
    """Schema for listing judges with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
