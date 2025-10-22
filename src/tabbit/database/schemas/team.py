"""Team database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class TeamCreate(BaseModel):
    """Schema for creating a team."""

    name: str
    abbreviation: str | None = None
    tournament_id: int


class Team(BaseModel):
    """Schema for a team with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str | None
    tournament_id: int


class TeamPatch(BaseModel):
    """Schema for partially updating a team."""

    name: str | None = None
    abbreviation: str | None = None


class ListTeamsQuery(BaseModel):
    """Schema for listing teams with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
