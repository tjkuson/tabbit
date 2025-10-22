"""Speaker database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class SpeakerCreate(BaseModel):
    """Schema for creating a speaker."""

    name: str
    team_id: int


class Speaker(BaseModel):
    """Schema for a speaker with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    team_id: int


class ListSpeakersQuery(BaseModel):
    """Schema for listing speakers with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    team_id: int | None = None
