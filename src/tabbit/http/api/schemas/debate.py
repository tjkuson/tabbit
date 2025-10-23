from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class DebateBase(BaseModel):
    """Shared debate properties."""

    round_id: int = Field(
        description="The round ID.",
        examples=[42],
    )


class DebateID(BaseModel):
    id: int = Field(
        description="The debate ID.",
        examples=[42],
    )


class DebateCreate(DebateBase):
    pass


class Debate(DebateBase, DebateID):
    model_config = ConfigDict(from_attributes=True)


class DebatePatch(BaseModel):
    round_id: int | None = Field(
        default=None,
        description="The updated round ID; not updated if unset.",
        examples=[42],
    )


class ListDebatesQuery(BaseModel):
    offset: int = Field(
        default=0,
        description="The number of records by which to offset.",
    )
    limit: int = Field(
        default=100,
        description="The maximum number of records to return.",
    )
    round_id: int | None = Field(
        default=None,
        description="Optional round ID filter to search for debates.",
    )
