"""Round database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict

from tabbit.database.enums import RoundStatus


class RoundCreate(BaseModel):
    """Schema for creating a round."""

    name: str
    abbreviation: str | None = None
    tournament_id: int
    sequence: int
    status: RoundStatus


class Round(BaseModel):
    """Schema for a round with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str | None
    tournament_id: int
    sequence: int
    status: RoundStatus


class RoundPatch(BaseModel):
    """Schema for partially updating a round."""

    name: str | None = None
    abbreviation: str | None = None
    sequence: int | None = None
    status: RoundStatus | None = None


class ListRoundsQuery(BaseModel):
    """Schema for listing rounds with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
    status: RoundStatus | None = None
