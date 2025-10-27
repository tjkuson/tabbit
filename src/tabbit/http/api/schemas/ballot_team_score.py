from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BallotTeamScoreBase(BaseModel):
    """Shared ballot team score properties."""

    ballot_id: int = Field(
        description="The ID of the ballot.",
        examples=[42],
    )
    team_id: int = Field(
        description="The ID of the team.",
        examples=[7],
    )
    score: int = Field(
        description="The score assigned to the team.",
        examples=[3, 2, 1, 0],
    )


class BallotTeamScoreID(BaseModel):
    id: int = Field(
        description="The unique identifier for this ballot team score entry.",
        examples=[42],
    )


class BallotTeamScoreCreate(BallotTeamScoreBase):
    pass


class BallotTeamScore(BallotTeamScoreBase, BallotTeamScoreID):
    model_config = ConfigDict(from_attributes=True)


class ListBallotTeamScoreQuery(BaseModel):
    offset: int = Field(
        default=0,
        description="The number of records by which to offset.",
    )
    limit: int = Field(
        default=100,
        description="The maximum number of records to return.",
    )
    ballot_id: int | None = Field(
        default=None,
        description="Optional ballot ID filter to search for team scores.",
    )
    team_id: int | None = Field(
        default=None,
        description="Optional team ID filter to search for team scores.",
    )
