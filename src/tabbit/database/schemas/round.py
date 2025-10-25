"""Round database schemas."""

from dataclasses import dataclass

from tabbit.database.enums import RoundStatus
from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class RoundCreate:
    """Schema for creating a round."""

    tournament_id: int
    sequence: int
    status: RoundStatus
    name: str
    abbreviation: str | None = None


@dataclass(frozen=True, slots=True)
class Round:
    """Schema for a round with ID."""

    id: int
    tournament_id: int
    sequence: int
    status: RoundStatus
    name: str
    abbreviation: str | None


@dataclass(frozen=True, slots=True)
class RoundPatch:
    """Schema for partially updating a round."""

    name: str | UnsetT = Unset
    abbreviation: str | None | UnsetT = Unset
    sequence: int | UnsetT = Unset
    status: RoundStatus | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListRoundsQuery:
    """Schema for listing rounds with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
    status: RoundStatus | None = None
