"""Ballot database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class BallotCreate(BaseModel):
    """Schema for creating a ballot."""

    debate_id: int
    judge_id: int
    version: int = 1


class Ballot(BaseModel):
    """Schema for a ballot with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    debate_id: int
    judge_id: int
    version: int


class BallotPatch(BaseModel):
    """Schema for patching a ballot."""

    version: int | None = None


class ListBallotsQuery(BaseModel):
    """Schema for listing ballots with filters."""

    offset: int = 0
    limit: int = 100
    debate_id: int | None = None
    judge_id: int | None = None
