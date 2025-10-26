"""Ballot speaker points database schemas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BallotSpeakerPointsCreate:
    """Schema for creating ballot speaker points."""

    ballot_id: int
    speaker_id: int
    speaker_position: int
    score: int


@dataclass(frozen=True, slots=True)
class BallotSpeakerPoints:
    """Schema for ballot speaker points with ID."""

    id: int
    ballot_id: int
    speaker_id: int
    speaker_position: int
    score: int


@dataclass(frozen=True, slots=True)
class ListBallotSpeakerPointsQuery:
    """Schema for listing ballot speaker points with filters."""

    offset: int = 0
    limit: int = 100
    ballot_id: int | None = None
    speaker_id: int | None = None
