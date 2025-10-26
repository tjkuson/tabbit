import enum
from typing import final


@final
class Tags(enum.StrEnum):
    BALLOT = "ballot"
    BALLOT_SPEAKER_POINTS = "ballot_speaker_points"
    DEBATE = "debate"
    JUDGE = "judge"
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
