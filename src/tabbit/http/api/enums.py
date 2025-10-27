import enum
from typing import final


@final
class Tags(enum.StrEnum):
    BALLOT = "ballot"
    BALLOT_SPEAKER_POINTS = "ballot_speaker_points"
    BALLOT_TEAM_SCORE = "ballot_team_score"
    DEBATE = "debate"
    JUDGE = "judge"
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"
