from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SpeakerBase(BaseModel):
    """Shared speaker properties."""

    name: str = Field(
        description="The full name of the speaker.",
        examples=["Jane Doe"],
    )
    team_id: int = Field(
        description="The team ID.",
        examples=[42],
    )


class SpeakerID(BaseModel):
    id: int = Field(
        description="The speaker ID.",
        examples=[42],
    )


class SpeakerCreate(SpeakerBase):
    pass


class Speaker(SpeakerBase, SpeakerID):
    model_config = ConfigDict(from_attributes=True)


class SpeakerPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated full name of the speaker; not updated if unset.",
        examples=["Jane Doe"],
    )


class ListSpeakersQuery(BaseModel):
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
        description="Optional name filter to search for speaker.",
    )
    team_id: int | None = Field(
        default=None,
        description="Optional team ID filter to search for a speaker.",
    )
