from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BallotSpeakerPointsBase(BaseModel):
    """Shared ballot speaker points properties."""

    ballot_id: int = Field(
        description="The ID of the ballot.",
        examples=[42],
    )
    speaker_id: int = Field(
        description="The ID of the speaker.",
        examples=[7],
    )
    speaker_position: int = Field(
        description="The speaking position of this speaker in the team.",
        examples=[1, 2, 3],
    )
    score: int = Field(
        description="The score assigned to the speaker.",
        examples=[72, 75, 78],
    )


class BallotSpeakerPointsID(BaseModel):
    id: int = Field(
        description="The unique identifier for this ballot speaker points entry.",
        examples=[42],
    )


class BallotSpeakerPointsCreate(BallotSpeakerPointsBase):
    pass


class BallotSpeakerPoints(BallotSpeakerPointsBase, BallotSpeakerPointsID):
    model_config = ConfigDict(from_attributes=True)


class ListBallotSpeakerPointsQuery(BaseModel):
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
        description="Optional ballot ID filter to search for speaker points.",
    )
    speaker_id: int | None = Field(
        default=None,
        description="Optional speaker ID filter to search for speaker points.",
    )
