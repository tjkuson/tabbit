from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TournamentBase(BaseModel):
    """Shared tournament properties."""

    name: str = Field(
        description="The name of the tournament.",
        examples=["World Universities Debating Championships 2025"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the tournament.",
        examples=["WUDC 2025"],
    )


class TournamentID(BaseModel):
    id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )


class TournamentCreate(TournamentBase):
    pass


class Tournament(TournamentBase, TournamentID):
    model_config = ConfigDict(from_attributes=True)


class TournamentPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated name of the tournament; not updated if unset.",
        examples=["World Universities Debating Championships 2025"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the tournament; not updated if unset.",
        examples=["WUDC 2025"],
    )


class ListTournamentsQuery(BaseModel):
    offset: int = Field(
        default=0,
        description="The number of records by which to offset.",
    )
    limit: int = Field(
        default=100,
        description="The maximum number of records to return.",
    )
    name: str | None = Field(
        default=None,
        description="Optional name filter to search for tournaments.",
    )
