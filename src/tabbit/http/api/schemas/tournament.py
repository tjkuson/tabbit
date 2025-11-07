from typing import Annotated

from pydantic import AfterValidator
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


def _valid_slug(slug: str) -> str:
    """Validate that slug contains only lowercase alphanumeric characters.

    Args:
        slug: The slug to validate.

    Returns:
        The validated slug.

    Raises:
        ValueError: If the slug is empty or contains invalid characters.
    """
    if not slug:
        msg = "Slug cannot be empty"
        raise ValueError(msg)

    for char in slug:
        if not (char.islower() or char.isdigit()):
            msg = f"Slug must contain only lowercase letters and digits, found '{char}'"
            raise ValueError(msg)

    return slug


SlugStr = Annotated[str, AfterValidator(_valid_slug)]


class TournamentBase(BaseModel):
    """Shared tournament properties."""

    name: str = Field(
        description="The name of the tournament.",
        examples=["World Universities Debating Championships 2025"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the tournament.",
        examples=["WUDC 2025"],
    )
    slug: SlugStr | None = Field(
        default=None,
        description=(
            "URL-friendly identifier for the tournament. Defaults to lowercase "
            "abbreviation (if present) or lowercase name (spaces removed). "
            "Must be unique."
        ),
        examples=["eudc2025", "oxfordiv2025"],
    )


class TournamentID(BaseModel):
    id: int = Field(
        description="The tournament ID.",
        examples=[42],
    )


class TournamentCreate(TournamentBase):
    pass


class Tournament(TournamentBase, TournamentID):
    model_config = ConfigDict(from_attributes=True)


class TournamentPatch(BaseModel):
    name: str | None = Field(
        default=None,
        description="The updated name of the tournament; not updated if unset.",
        examples=["World Universities Debating Championships 2025"],
    )
    abbreviation: str | None = Field(
        default=None,
        description="The abbreviated name of the tournament; not updated if unset.",
        examples=["WUDC 2025"],
    )
    slug: SlugStr | None = Field(
        default=None,
        description="URL-friendly identifier for the tournament; not updated if unset.",
        examples=["eudc2025", "oxfordiv2025"],
    )


class ListTournamentsQuery(BaseModel):
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
        description="Optional name filter to search for tournaments.",
    )
