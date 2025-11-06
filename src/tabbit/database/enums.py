import enum
from typing import final


@final
class TableName(enum.StrEnum):
    BALLOT = "ballot"
    BALLOT_SPEAKER_POINTS = "ballot_speaker_points"
    BALLOT_TEAM_SCORE = "ballot_team_score"
    DEBATE = "debate"
    JUDGE = "judge"
    JUDGE_TAG = "judge_tag"
    MOTION = "motion"
    ROUND = "round"
    SPEAKER = "speaker"
    SPEAKER_TAG = "speaker_tag"
    TAG = "tag"
    TEAM = "team"
    TOURNAMENT = "tournament"


@final
class RoundStatus(enum.StrEnum):
    """Status values for a round."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
