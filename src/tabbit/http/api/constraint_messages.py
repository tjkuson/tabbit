from typing import Final

from sqlalchemy.exc import IntegrityError

_UNIQUE_CONSTRAINT_PATTERNS: Final = (
    (
        "team.tournament_id, team.name",
        "A team with this name already exists in this tournament",
    ),
    (
        "round.tournament_id, round.sequence",
        "A round with this sequence already exists in this tournament",
    ),
    (
        "ballot_speaker_points.ballot_id, ballot_speaker_points.speaker_id",
        "This speaker already has points recorded for this ballot",
    ),
    (
        "ballot_team_score.ballot_id, ballot_team_score.team_id",
        "This team already has a score recorded for this ballot",
    ),
    (
        "tag.tournament_id, tag.name",
        "A tag with this name already exists in this tournament",
    ),
    (
        "speaker_tag.speaker_id, speaker_tag.tag_id",
        "This speaker is already associated with this tag",
    ),
    (
        "judge_tag.judge_id, judge_tag.tag_id",
        "This judge is already associated with this tag",
    ),
    (
        "tournament.slug",
        "A tournament with this slug already exists",
    ),
)
_UNIQUE_CONSTRAINT_MESSAGES: Final = {
    f"UNIQUE constraint failed: {key}": value
    for key, value in _UNIQUE_CONSTRAINT_PATTERNS
}
_CONSTRAINT_MESSAGES: Final = _UNIQUE_CONSTRAINT_MESSAGES | {
    "FOREIGN KEY constraint failed": "Referenced resource does not exist",
}


def get_constraint_violation_message(exc: IntegrityError) -> str:
    """Parse IntegrityError and return user-friendly message.

    Args:
        exc: The IntegrityError from SQLAlchemy.

    Returns:
        A user-friendly error message describing the constraint violation.
    """
    error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    return _CONSTRAINT_MESSAGES.get(error_msg, "Database constraint violated")
