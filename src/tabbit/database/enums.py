import enum
from typing import final


@final
class TableName(enum.StrEnum):
    BALLOT = "ballot"
    DEBATE = "debate"
    JUDGE = "judge"
    ROUND = "round"
    SPEAKER = "speaker"
    TEAM = "team"
    TOURNAMENT = "tournament"


@final
class RoundStatus(enum.StrEnum):
    """Status values for a round."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
