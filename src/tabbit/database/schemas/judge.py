"""Judge database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class JudgeCreate(BaseModel):
    """Schema for creating a judge."""

    name: str
    tournament_id: int


class Judge(BaseModel):
    """Schema for a judge with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tournament_id: int


class ListJudgesQuery(BaseModel):
    """Schema for listing judges with filters."""

    offset: int = 0
    limit: int = 100
    name: str | None = None
    tournament_id: int | None = None
