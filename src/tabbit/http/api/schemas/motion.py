from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class MotionBase(BaseModel):
    """Shared motion properties."""

    round_id: int = Field(
        description="The round ID.",
        examples=[42],
    )
    text: str = Field(
        description="The motion text.",
        examples=["This House would ban zoos."],
    )
    infoslide: str | None = Field(
        default=None,
        description="The infoslide providing additional context for the motion.",
        examples=["Zoos are facilities where animals are kept in captivity."],
    )


class MotionID(BaseModel):
    id: int = Field(
        description="The motion ID.",
        examples=[42],
    )


class MotionCreate(MotionBase):
    pass


class Motion(MotionBase, MotionID):
    model_config = ConfigDict(from_attributes=True)


class MotionPatch(BaseModel):
    text: str | None = Field(
        default=None,
        description="The updated motion text; not updated if unset.",
        examples=["This House would legalise all drugs."],
    )
    infoslide: str | None = Field(
        default=None,
        description="The updated infoslide; not updated if unset.",
        examples=["Updated infoslide text."],
    )


class ListMotionsQuery(BaseModel):
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
        description="Optional round ID filter to search for motions.",
    )
    text: str | None = Field(
        default=None,
        description="Optional text filter to search for motions.",
    )
