"""Tournament database schemas."""

from dataclasses import dataclass

from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class TournamentCreate:
    """Schema for creating a tournament."""

    name: str
    abbreviation: str | None = None
    slug: str | None = None


@dataclass(frozen=True, slots=True)
class Tournament:
    """Schema for a tournament with ID."""

    id: int
    name: str
    abbreviation: str | None
    slug: str


@dataclass(frozen=True, slots=True)
class TournamentPatch:
    """Schema for partially updating a tournament."""

    name: str | UnsetT = Unset
    abbreviation: str | None | UnsetT = Unset
    slug: str | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListTournamentsQuery:
    """Schema for listing tournaments with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
