from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class JudgeBase(BaseModel):
    """Shared judge properties."""

    name: str = Field(
        description="The full name of the judge.",
        examples=["Jane Smith"],
    )
    tournament_id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )


class JudgeID(BaseModel):
    id: int = Field(
        description="The judge ID.",
        examples=[42],
    )


class JudgeCreate(JudgeBase):
    pass


class Judge(JudgeBase, JudgeID):
    model_config = ConfigDict(from_attributes=True)


class JudgePatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated full name of the judge; not updated if unset.",
        examples=["Jane Smith"],
    )


class ListJudgesQuery(BaseModel):
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
        description="Optional name filter to search for judge.",
    )
    tournament_id: int | None = Field(
        default=None,
        description="Optional tournament ID filter to search for a judge.",
    )
