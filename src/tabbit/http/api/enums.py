import enum
from typing import final


@final
class Tags(enum.StrEnum):
    BALLOT = "ballot"
    DEBATE = "debate"
    JUDGE = "judge"
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
