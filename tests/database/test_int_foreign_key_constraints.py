import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.ballot import create_ballot
from tabbit.database.operations.ballot_speaker_points import (
    create_ballot_speaker_points,
)
from tabbit.database.operations.ballot_team_score import create_ballot_team_score
from tabbit.database.operations.debate import create_debate
from tabbit.database.operations.judge import create_judge
from tabbit.database.operations.motion import create_motion
from tabbit.database.operations.round import create_round
from tabbit.database.operations.speaker import create_speaker
from tabbit.database.operations.team import create_team
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.schemas.ballot import BallotCreate
from tabbit.database.schemas.ballot_speaker_points import BallotSpeakerPointsCreate
from tabbit.database.schemas.ballot_team_score import BallotTeamScoreCreate
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.motion import MotionCreate
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.speaker import SpeakerCreate
from tabbit.database.schemas.team import TeamCreate
from tabbit.database.schemas.tournament import TournamentCreate

NONEXISTENT_ID = 99999


@pytest.mark.asyncio
async def test_pragma_foreign_keys_enabled(session: AsyncSession) -> None:
    """PRAGMA foreign_keys is enabled for the database connection."""
    result = await session.execute(text("PRAGMA foreign_keys"))
    foreign_keys_status = result.scalar()
    assert foreign_keys_status == 1, "Foreign key constraints are not enabled"


@pytest.mark.asyncio
async def test_team_invalid_tournament_id(session: AsyncSession) -> None:
    """Creating a team with non-existent tournament_id fails."""
    team_create = TeamCreate(
        name="Test Team",
        abbreviation="TT",
        tournament_id=NONEXISTENT_ID,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_team(session, team_create)


@pytest.mark.asyncio
async def test_speaker_invalid_team_id(session: AsyncSession) -> None:
    """Creating a speaker with non-existent team_id fails."""
    speaker_create = SpeakerCreate(
        name="Test Speaker",
        team_id=NONEXISTENT_ID,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_speaker(session, speaker_create)


@pytest.mark.asyncio
async def test_judge_invalid_tournament_id(session: AsyncSession) -> None:
    """Creating a judge with non-existent tournament_id fails."""
    judge_create = JudgeCreate(
        name="Test Judge",
        tournament_id=NONEXISTENT_ID,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_judge(session, judge_create)


@pytest.mark.asyncio
async def test_round_invalid_tournament_id(session: AsyncSession) -> None:
    """Creating a round with non-existent tournament_id fails."""
    round_create = RoundCreate(
        name="Round 1",
        abbreviation="R1",
        sequence=1,
        status=RoundStatus.DRAFT,
        tournament_id=NONEXISTENT_ID,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_round(session, round_create)


@pytest.mark.asyncio
async def test_motion_invalid_round_id(session: AsyncSession) -> None:
    """Creating a motion with non-existent round_id fails."""
    motion_create = MotionCreate(
        text="This house believes that...",
        infoslide="Context information",
        round_id=NONEXISTENT_ID,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_motion(session, motion_create)


@pytest.mark.asyncio
async def test_debate_invalid_round_id(session: AsyncSession) -> None:
    """Creating a debate with non-existent round_id fails."""
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_debate(session, round_id=NONEXISTENT_ID)


@pytest.mark.asyncio
async def test_ballot_invalid_debate_id(session: AsyncSession) -> None:
    """Creating a ballot with non-existent debate_id fails."""
    # Create valid tournament and judge
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    judge_create = JudgeCreate(
        name="Test Judge",
        tournament_id=tournament_id,
    )
    judge_id = await create_judge(session, judge_create)

    # Try to create ballot with invalid debate_id
    ballot_create = BallotCreate(
        debate_id=NONEXISTENT_ID,
        judge_id=judge_id,
        version=1,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot(session, ballot_create)


@pytest.mark.asyncio
async def test_ballot_invalid_judge_id(session: AsyncSession) -> None:
    """Creating a ballot with non-existent judge_id fails."""
    # Create valid tournament, round, and debate
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name="Round 1",
        abbreviation="R1",
        sequence=1,
        status=RoundStatus.DRAFT,
        tournament_id=tournament_id,
    )
    round_id = await create_round(session, round_create)
    debate_id = await create_debate(session, round_id=round_id)

    # Try to create ballot with invalid judge_id
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=NONEXISTENT_ID,
        version=1,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot(session, ballot_create)


@pytest.mark.asyncio
async def test_ballot_speaker_points_invalid_ballot_id(
    session: AsyncSession,
) -> None:
    """Creating ballot speaker points with non-existent ballot_id fails."""
    # Create valid tournament, team, and speaker
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name="Test Team",
        abbreviation="TT",
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    speaker_create = SpeakerCreate(
        name="Test Speaker",
        team_id=team_id,
    )
    speaker_id = await create_speaker(session, speaker_create)

    # Try to create ballot speaker points with invalid ballot_id
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=NONEXISTENT_ID,
        speaker_id=speaker_id,
        speaker_position=1,
        score=75,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot_speaker_points(session, ballot_speaker_points_create)


@pytest.mark.asyncio
async def test_ballot_speaker_points_invalid_speaker_id(
    session: AsyncSession,
) -> None:
    """Creating ballot speaker points with non-existent speaker_id fails."""
    # Create valid tournament, round, debate, judge, and ballot
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name="Round 1",
        abbreviation="R1",
        sequence=1,
        status=RoundStatus.DRAFT,
        tournament_id=tournament_id,
    )
    round_id = await create_round(session, round_create)
    debate_id = await create_debate(session, round_id=round_id)
    judge_create = JudgeCreate(
        name="Test Judge",
        tournament_id=tournament_id,
    )
    judge_id = await create_judge(session, judge_create)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=1,
    )
    ballot_id = await create_ballot(session, ballot_create)

    # Try to create ballot speaker points with invalid speaker_id
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=NONEXISTENT_ID,
        speaker_position=1,
        score=75,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot_speaker_points(session, ballot_speaker_points_create)


@pytest.mark.asyncio
async def test_ballot_team_score_invalid_ballot_id(session: AsyncSession) -> None:
    """Creating ballot team score with non-existent ballot_id fails."""
    # Create valid tournament and team
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name="Test Team",
        abbreviation="TT",
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)

    # Try to create ballot team score with invalid ballot_id
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=NONEXISTENT_ID,
        team_id=team_id,
        score=3,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot_team_score(session, ballot_team_score_create)


@pytest.mark.asyncio
async def test_ballot_team_score_invalid_team_id(session: AsyncSession) -> None:
    """Creating ballot team score with non-existent team_id fails."""
    # Create valid tournament, round, debate, judge, and ballot
    tournament_create = TournamentCreate(
        name="Test Tournament",
        abbreviation="TT",
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name="Round 1",
        abbreviation="R1",
        sequence=1,
        status=RoundStatus.DRAFT,
        tournament_id=tournament_id,
    )
    round_id = await create_round(session, round_create)
    debate_id = await create_debate(session, round_id=round_id)
    judge_create = JudgeCreate(
        name="Test Judge",
        tournament_id=tournament_id,
    )
    judge_id = await create_judge(session, judge_create)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=1,
    )
    ballot_id = await create_ballot(session, ballot_create)

    # Try to create ballot team score with invalid team_id
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=NONEXISTENT_ID,
        score=3,
    )
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        await create_ballot_team_score(session, ballot_team_score_create)
