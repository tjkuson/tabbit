import enum
from typing import final


@final
class Tags(enum.StrEnum):
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
