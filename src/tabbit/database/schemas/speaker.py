"""Speaker database schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpeakerCreate:
    """Schema for creating a speaker."""

    team_id: int
    name: str


@dataclass(frozen=True, slots=True)
class Speaker:
    """Schema for a speaker with ID."""

    id: int
    team_id: int
    name: str


@dataclass(frozen=True, slots=True)
class ListSpeakersQuery:
    """Schema for listing speakers with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    team_id: int | None = None
