"""Ballot team score database schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BallotTeamScoreCreate:
    """Schema for creating ballot team score."""

    ballot_id: int
    team_id: int
    score: int


@dataclass(frozen=True, slots=True)
class BallotTeamScore:
    """Schema for ballot team score with ID."""

    id: int
    ballot_id: int
    team_id: int
    score: int


@dataclass(frozen=True, slots=True)
class ListBallotTeamScoreQuery:
    """Schema for listing ballot team scores with filters."""

    offset: int = 0
    limit: int = 100
    ballot_id: int | None = None
    team_id: int | None = None
