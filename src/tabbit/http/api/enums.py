import enum
from typing import final


@final
class Tags(enum.StrEnum):
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
