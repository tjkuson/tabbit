from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TagBase(BaseModel):
    """Shared tag properties."""

    name: str = Field(
        description="The name of the tag.",
        examples=[
            "Manchester Debating Union",
            "English as a Second Language",
        ],
    )
    tournament_id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )


class TagID(BaseModel):
    id: int = Field(
        description="The tag ID.",
        examples=[42],
    )


class TagCreate(TagBase):
    pass


class Tag(TagBase, TagID):
    model_config = ConfigDict(from_attributes=True)


class TagPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated name of the tag; not updated if unset.",
        examples=["Expert"],
    )


class ListTagsQuery(BaseModel):
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
        description="Optional name filter to search for tags.",
    )
    tournament_id: int | None = Field(
        default=None,
        description="Optional tournament ID filter to search for tags.",
    )
    speaker_id: int | None = Field(
        default=None,
        description="Optional speaker ID filter to search for tags.",
    )
    judge_id: int | None = Field(
        default=None,
        description="Optional judge ID filter to search for tags.",
    )


class AddSpeakersToTag(BaseModel):
    speaker_ids: list[int] = Field(
        description="The IDs of the speakers to add to the tag.",
        examples=[[1, 2, 3]],
    )


class AddJudgesToTag(BaseModel):
    judge_ids: list[int] = Field(
        description="The IDs of the judges to add to the tag.",
        examples=[[1, 2, 3]],
    )
