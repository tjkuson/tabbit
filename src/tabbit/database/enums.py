import enum
from typing import final


@final
class TableName(enum.StrEnum):
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
