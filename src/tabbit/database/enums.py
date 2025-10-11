from __future__ import annotations

import enum
from typing import final


@final
class TableName(enum.StrEnum):
    TEAM = "team"
    TOURNAMENT = "tournament"
