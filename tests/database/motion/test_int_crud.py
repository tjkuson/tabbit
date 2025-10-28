import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.motion import create_motion
from tabbit.database.operations.motion import delete_motion
from tabbit.database.operations.motion import get_motion
from tabbit.database.operations.motion import list_motions
from tabbit.database.operations.motion import patch_motion
from tabbit.database.operations.round import create_round
from tabbit.database.operations.round import delete_round
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.schemas.motion import ListMotionsQuery
from tabbit.database.schemas.motion import MotionCreate
from tabbit.database.schemas.motion import MotionPatch
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION = "EUDC 2025"
ROUND_NAME = "Round 1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT
MOTION_TEXT = "This House would ban zoos."
MOTION_INFOSLIDE = (
    "Zoos are facilities where animals are kept in captivity for public viewing."
)


async def _setup_data(session: AsyncSession) -> tuple[int, int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    motion_create = MotionCreate(
        round_id=round_id,
        text=MOTION_TEXT,
        infoslide=MOTION_INFOSLIDE,
    )
    motion_id = await create_motion(session, motion_create)
    return tournament_id, round_id, motion_id


@pytest.mark.asyncio
async def test_motion_create(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    motion_create = MotionCreate(
        round_id=round_id,
        text=MOTION_TEXT,
        infoslide=MOTION_INFOSLIDE,
    )
    motion_id = await create_motion(session, motion_create)
    assert isinstance(motion_id, int)


@pytest.mark.asyncio
async def test_motion_create_without_infoslide(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    motion_create = MotionCreate(
        round_id=round_id,
        text=MOTION_TEXT,
        infoslide=None,
    )
    motion_id = await create_motion(session, motion_create)
    assert isinstance(motion_id, int)

    # Verify infoslide is None
    motion = await get_motion(session, motion_id)
    assert motion is not None
    assert motion.infoslide is None


@pytest.mark.asyncio
async def test_motion_read(session: AsyncSession) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(session)
    motion = await get_motion(session, motion_id)
    assert motion is not None
    assert motion.id == motion_id
    assert motion.round_id == round_id
    assert motion.text == MOTION_TEXT
    assert motion.infoslide == MOTION_INFOSLIDE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("patch", "expected_text", "expected_infoslide"),
    [
        (
            MotionPatch(text="This House would legalise all drugs."),
            "This House would legalise all drugs.",
            MOTION_INFOSLIDE,
        ),
        (
            MotionPatch(infoslide="Updated infoslide text."),
            MOTION_TEXT,
            "Updated infoslide text.",
        ),
        (
            MotionPatch(infoslide=None),
            MOTION_TEXT,
            None,
        ),
        (
            MotionPatch(
                text="This House supports universal basic income.",
                infoslide="UBI is a payment to all citizens.",
            ),
            "This House supports universal basic income.",
            "UBI is a payment to all citizens.",
        ),
    ],
)
async def test_motion_update(
    session: AsyncSession,
    patch: MotionPatch,
    expected_text: str,
    expected_infoslide: str | None,
) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(session)

    motion = await patch_motion(session, motion_id, patch)
    assert motion is not None
    assert motion.id == motion_id
    assert motion.round_id == round_id
    assert motion.text == expected_text
    assert motion.infoslide == expected_infoslide

    # Read (to check the update persists)
    motion = await get_motion(session, motion_id)
    assert motion is not None
    assert motion.id == motion_id
    assert motion.round_id == round_id
    assert motion.text == expected_text
    assert motion.infoslide == expected_infoslide


@pytest.mark.asyncio
async def test_round_delete_cascades_to_motion(session: AsyncSession) -> None:
    """Test that deleting a round cascades to delete its motions."""
    _tournament_id, round_id, motion_id = await _setup_data(session)
    deleted_round_id = await delete_round(session, round_id)
    assert deleted_round_id == round_id

    motion = await get_motion(session, motion_id)
    assert motion is None


@pytest.mark.asyncio
async def test_motion_delete(session: AsyncSession) -> None:
    _tournament_id, _round_id, motion_id = await _setup_data(session)
    deleted_motion_id = await delete_motion(session, motion_id)
    assert deleted_motion_id == motion_id

    motion = await get_motion(session, motion_id)
    assert motion is None


@pytest.mark.asyncio
async def test_motion_list_empty(session: AsyncSession) -> None:
    motions = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(),
    )
    assert motions == []


@pytest.mark.asyncio
async def test_motion_list(session: AsyncSession) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(session)
    motions = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(),
    )
    assert len(motions) == 1
    assert motions[0].id == motion_id
    assert motions[0].round_id == round_id
    assert motions[0].text == MOTION_TEXT
    assert motions[0].infoslide == MOTION_INFOSLIDE


@pytest.mark.asyncio
async def test_motion_list_round_filter(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)

    # Create two rounds with motions
    first_round_id = await create_round(
        session,
        RoundCreate(
            name="Round 1",
            tournament_id=tournament_id,
            sequence=1,
            status=ROUND_STATUS,
        ),
    )
    first_motion_id = await create_motion(
        session,
        MotionCreate(
            round_id=first_round_id,
            text="First motion",
            infoslide=None,
        ),
    )

    second_round_id = await create_round(
        session,
        RoundCreate(
            name="Round 2",
            tournament_id=tournament_id,
            sequence=2,
            status=ROUND_STATUS,
        ),
    )
    second_motion_id = await create_motion(
        session,
        MotionCreate(
            round_id=second_round_id,
            text="Second motion",
            infoslide=None,
        ),
    )

    # Test filtering by first round
    motions = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(round_id=first_round_id),
    )
    assert len(motions) == 1
    assert motions[0].id == first_motion_id
    assert motions[0].round_id == first_round_id

    # Test filtering by second round
    motions = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(round_id=second_round_id),
    )
    assert len(motions) == 1
    assert motions[0].id == second_motion_id
    assert motions[0].round_id == second_round_id


@pytest.mark.asyncio
async def test_motion_list_offset(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_id = await create_round(
        session,
        RoundCreate(
            name=ROUND_NAME,
            tournament_id=tournament_id,
            sequence=ROUND_SEQUENCE,
            status=ROUND_STATUS,
        ),
    )
    _first_motion_id = await create_motion(
        session,
        MotionCreate(round_id=round_id, text="First", infoslide=None),
    )
    last_motion_id = await create_motion(
        session,
        MotionCreate(round_id=round_id, text="Last", infoslide=None),
    )

    result = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(offset=1),
    )
    assert len(result) == 1
    assert result[0].id == last_motion_id
    assert result[0].text == "Last"


@pytest.mark.parametrize(
    ("insert_n", "limit", "expect_n"),
    [
        (0, 0, 0),
        (0, 1, 0),
        (1, 0, 0),
        (1, 2, 1),
        (2, 1, 1),
        (1, 1, 1),
    ],
)
@pytest.mark.asyncio
async def test_motion_list_limit(
    session: AsyncSession,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_id = await create_round(
        session,
        RoundCreate(
            name=ROUND_NAME,
            tournament_id=tournament_id,
            sequence=ROUND_SEQUENCE,
            status=ROUND_STATUS,
        ),
    )
    for idx in range(insert_n):
        _ = await create_motion(
            session,
            MotionCreate(
                round_id=round_id,
                text=f"Motion {idx}",
                infoslide=None,
            ),
        )
    result = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(limit=limit),
    )
    assert len(result) == expect_n


@pytest.mark.parametrize(
    ("insert_texts", "text_filter", "expect_texts"),
    [
        ([], "", []),
        ([], "House", []),
        (["This House would ban zoos."], "", ["This House would ban zoos."]),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "ban",
            ["This House would ban zoos."],
        ),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "House",
            ["This House would ban zoos.", "This House supports cats."],
        ),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "HOUSE",
            ["This House would ban zoos.", "This House supports cats."],
        ),
    ],
)
@pytest.mark.asyncio
async def test_motion_list_text_filter(
    session: AsyncSession,
    insert_texts: list[str],
    text_filter: str,
    expect_texts: list[str],
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_id = await create_round(
        session,
        RoundCreate(
            name=ROUND_NAME,
            tournament_id=tournament_id,
            sequence=ROUND_SEQUENCE,
            status=ROUND_STATUS,
        ),
    )
    for text in insert_texts:
        _ = await create_motion(
            session,
            MotionCreate(
                round_id=round_id,
                text=text,
                infoslide=None,
            ),
        )
    result = await list_motions(
        session,
        list_motions_query=ListMotionsQuery(text=text_filter),
    )
    texts = [motion.text for motion in result]
    assert texts == expect_texts


@pytest.mark.asyncio
async def test_motion_get_missing(session: AsyncSession) -> None:
    motion = await get_motion(
        session,
        motion_id=1,
    )
    assert motion is None


@pytest.mark.asyncio
async def test_motion_delete_missing(session: AsyncSession) -> None:
    motion_id = await delete_motion(
        session,
        motion_id=1,
    )
    assert motion_id is None


@pytest.mark.asyncio
async def test_motion_patch_missing(session: AsyncSession) -> None:
    patch = MotionPatch(text="Missing")
    motion = await patch_motion(
        session,
        motion_id=1,
        motion_patch=patch,
    )
    assert motion is None
