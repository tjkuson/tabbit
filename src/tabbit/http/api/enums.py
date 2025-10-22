import enum
from typing import final


@final
class Tags(enum.StrEnum):
    DEBATE = "debate"
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
