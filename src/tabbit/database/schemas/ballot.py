"""Ballot database schemas."""

from dataclasses import dataclass

from tabbit.sentinel import Unset
from tabbit.sentinel import UnsetT


@dataclass(frozen=True, slots=True)
class BallotCreate:
    """Schema for creating a ballot."""

    debate_id: int
    judge_id: int
    version: int = 1


@dataclass(frozen=True, slots=True)
class Ballot:
    """Schema for a ballot with ID."""

    id: int
    debate_id: int
    judge_id: int
    version: int


@dataclass(frozen=True, slots=True)
class BallotPatch:
    """Schema for patching a ballot."""

    version: int | UnsetT = Unset


@dataclass(frozen=True, slots=True)
class ListBallotsQuery:
    """Schema for listing ballots with filters."""

    offset: int = 0
    limit: int = 100
    debate_id: int | None = None
    judge_id: int | None = None
