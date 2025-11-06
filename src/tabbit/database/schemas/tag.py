"""Tag database schemas."""

from dataclasses import dataclass

from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class TagCreate:
    """Schema for creating a tag."""

    tournament_id: int
    name: str


@dataclass(frozen=True, slots=True)
class Tag:
    """Schema for a tag with ID."""

    id: int
    tournament_id: int
    name: str


@dataclass(frozen=True, slots=True)
class TagPatch:
    """Schema for partially updating a tag."""

    name: str | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListTagsQuery:
    """Schema for listing tags with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
    speaker_id: int | None = None
    judge_id: int | None = None
