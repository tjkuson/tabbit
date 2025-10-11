from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TeamBase(BaseModel):
    """Shared tournament properties."""

    name: str = Field(
        description="The full name of the team.",
        examples=["Edinburgh University Debates Union A"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the team.",
        examples=["EUDU A"],
    )
    tournament_id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )


class TeamID(BaseModel):
    id: int = Field(
        description="The team ID.",
        examples=[42],
    )


class TeamCreate(TeamBase):
    pass


class Team(TeamBase, TeamID):
    model_config = ConfigDict(from_attributes=True)


class TeamPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated full name of the team; not updated if unset.",
        examples=["Edinburgh University Debates Union A"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the team; not updated if unset.",
        examples=["EUDU A"],
    )


class ListTeamsQuery(BaseModel):
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
        description="Optional name filter to search for team.",
    )
    tournament_id: int | None = Field(
        default=None,
        description="Optional tournament ID filter to search for a team.",
    )
