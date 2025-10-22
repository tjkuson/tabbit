from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from tabbit.database.enums import RoundStatus


class RoundBase(BaseModel):
    """Shared round properties."""

    name: str = Field(
        description="The full name of the round.",
        examples=["Round 1"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the round.",
        examples=["R1"],
    )
    tournament_id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )
    sequence: int = Field(
        description=(
            "The sequence number of the round (determines order, starts from 1)."
        ),
        examples=[1],
    )
    status: RoundStatus = Field(
        description="The status of the round.",
        examples=[RoundStatus.DRAFT],
    )


class RoundID(BaseModel):
    id: int = Field(
        description="The round ID.",
        examples=[42],
    )


class RoundCreate(RoundBase):
    pass


class Round(RoundBase, RoundID):
    model_config = ConfigDict(from_attributes=True)


class RoundPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated full name of the round; not updated if unset.",
        examples=["Round 1"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the round; not updated if unset.",
        examples=["R1"],
    )
    sequence: int | None = Field(
        default=None,
        description="The updated sequence number; not updated if unset.",
        examples=[1],
    )
    status: RoundStatus | None = Field(
        default=None,
        description="The updated status; not updated if unset.",
        examples=[RoundStatus.DRAFT],
    )


class ListRoundsQuery(BaseModel):
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
        description="Optional name filter to search for round.",
    )
    tournament_id: int | None = Field(
        default=None,
        description="Optional tournament ID filter to search for a round.",
    )
    status: RoundStatus | None = Field(
        default=None,
        description="Optional status filter to search for rounds.",
    )
