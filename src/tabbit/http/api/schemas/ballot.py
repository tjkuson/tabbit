from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BallotBase(BaseModel):
    """Shared ballot properties."""

    debate_id: int = Field(
        description="The ID of the debate this ballot is for.",
        examples=[42],
    )
    judge_id: int = Field(
        description="The ID of the judge who submitted this ballot.",
        examples=[7],
    )
    version: int = Field(
        default=1,
        description="The version number of this ballot (incremented on updates).",
        examples=[1, 2, 3],
    )


class BallotID(BaseModel):
    id: int = Field(
        description="The unique identifier for this ballot.",
        examples=[42],
    )


class BallotCreate(BallotBase):
    pass


class Ballot(BallotBase, BallotID):
    model_config = ConfigDict(from_attributes=True)


class BallotPatch(BaseModel):
    version: int | None = Field(
        default=None,
        description="The new version number for this ballot; not updated if unset.",
        examples=[2],
    )


class ListBallotsQuery(BaseModel):
    offset: int = Field(
        default=0,
        description="The number of records by which to offset.",
    )
    limit: int = Field(
        default=100,
        description="The maximum number of records to return.",
    )
    debate_id: int | None = Field(
        default=None,
        description="Optional debate ID filter to search for ballots.",
    )
    judge_id: int | None = Field(
        default=None,
        description="Optional judge ID filter to search for ballots.",
    )
