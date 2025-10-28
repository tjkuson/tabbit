"""Motion database schemas."""

from dataclasses import dataclass

from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class MotionCreate:
    """Schema for creating a motion."""

    round_id: int
    text: str
    infoslide: str | None = None


@dataclass(frozen=True, slots=True)
class Motion:
    """Schema for a motion with ID."""

    id: int
    round_id: int
    text: str
    infoslide: str | None


@dataclass(frozen=True, slots=True)
class MotionPatch:
    """Schema for partially updating a motion."""

    text: str | UnsetT = Unset
    infoslide: str | None | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListMotionsQuery:
    """Schema for listing motions with filters."""

    offset: int = 0
    limit: int = 100
    round_id: int | None = None
    text: str | None = None
