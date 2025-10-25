"""Team database schemas."""

from dataclasses import dataclass

from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class TeamCreate:
    """Schema for creating a team."""

    tournament_id: int
    name: str
    abbreviation: str | None = None


@dataclass(frozen=True, slots=True)
class Team:
    """Schema for a team with ID."""

    id: int
    tournament_id: int
    name: str
    abbreviation: str | None


@dataclass(frozen=True, slots=True)
class TeamPatch:
    """Schema for partially updating a team."""

    name: str | UnsetT = Unset
    abbreviation: str | None | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListTeamsQuery:
    """Schema for listing teams with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
