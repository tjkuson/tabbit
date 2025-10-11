import enum
from typing import final


@final
class TableName(enum.StrEnum):
    TEAM = "team"
    TOURNAMENT = "tournament"
