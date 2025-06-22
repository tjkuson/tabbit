from __future__ import annotations

import pytest
from pydantic import BaseModel

from tabbit.database import models
from tabbit.schemas.tournament import Tournament


@pytest.mark.parametrize(
    ("model", "schema"),
    [
        (
            models.Tournament(
                id=1,
                name="Manchester IV 2025",
                abbreviation=None,
            ),
            Tournament(
                id=1,
                name="Manchester IV 2025",
                abbreviation=None,
            ),
        ),
        (
            models.Tournament(
                id=1,
                name="World Universities Debating Championship 2025",
                abbreviation="WUDC 2025",
            ),
            Tournament(
                id=1,
                name="World Universities Debating Championship 2025",
                abbreviation="WUDC 2025",
            ),
        ),
    ],
)
def test_conversion(model: models.Base, schema: BaseModel) -> None:
    assert type(schema).model_validate(model) == schema, (
        "Expected to be able to convert from SQL representation to Pydantic"
        " representation."
    )
