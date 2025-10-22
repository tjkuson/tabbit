"""Debate database schemas."""

from pydantic import BaseModel
from pydantic import ConfigDict


class Debate(BaseModel):
    """Schema for a debate with ID."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    round_id: int


class ListDebatesQuery(BaseModel):
    """Schema for listing debates with filters."""

    offset: int = 0
    limit: int = 100
    round_id: int | None = None
