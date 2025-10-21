import enum
from typing import final


@final
class TableName(enum.StrEnum):
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
