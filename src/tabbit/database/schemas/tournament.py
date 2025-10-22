"""Tournament database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class TournamentCreate(BaseModel):
    """Schema for creating a tournament."""

    name: str
    abbreviation: str | None = None


class Tournament(BaseModel):
    """Schema for a tournament with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str | None


class TournamentPatch(BaseModel):
    """Schema for partially updating a tournament."""

    name: str | None = None
    abbreviation: str | None = None


class ListTournamentsQuery(BaseModel):
    """Schema for listing tournaments with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
