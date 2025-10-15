import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations.speaker import create_speaker
from tabbit.database.operations.speaker import delete_speaker
from tabbit.database.operations.speaker import get_speaker
from tabbit.database.operations.speaker import list_speakers
from tabbit.database.operations.speaker import patch_speaker
from tabbit.database.operations.team import create_team
from tabbit.database.operations.team import delete_team
from tabbit.database.operations.tournament import create_tournament
from tabbit.schemas.speaker import ListSpeakersQuery
from tabbit.schemas.speaker import SpeakerCreate
from tabbit.schemas.speaker import SpeakerPatch
from tabbit.schemas.team import TeamCreate
from tabbit.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION = "EUDC 2025"
TEAM_NAME = "Manchester Debating Union A"
TEAM_ABBREVIATION = "Manchester A"
SPEAKER_NAME = "Jane Doe"


async def _setup_data(session: AsyncSession) -> tuple[int, int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    speaker_create = SpeakerCreate(
        name=SPEAKER_NAME,
        team_id=team_id,
    )
    speaker_id = await create_speaker(session, speaker_create)
    return tournament_id, team_id, speaker_id


@pytest.mark.asyncio
async def test_speaker_create(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME, abbreviation=TOURNAMENT_ABBREVIATION
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    speaker_create = SpeakerCreate(
        name=SPEAKER_NAME,
        team_id=team_id,
    )
    speaker_id = await create_speaker(session, speaker_create)
    assert isinstance(speaker_id, int)


@pytest.mark.asyncio
async def test_speaker_read(session: AsyncSession) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(session)
    speaker = await get_speaker(session, speaker_id)
    assert speaker is not None
    assert speaker.name == SPEAKER_NAME
    assert speaker.team_id == team_id


@pytest.mark.asyncio
async def test_speaker_update(session: AsyncSession) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(session)

    new_name = "John Smith"
    patch = SpeakerPatch(name=new_name)
    speaker = await patch_speaker(session, speaker_id, patch)
    assert speaker is not None
    assert speaker.name == new_name
    assert speaker.id == speaker_id
    assert speaker.team_id == team_id

    # Read (to check the update persists).
    speaker = await get_speaker(session, speaker_id)
    assert speaker is not None
    assert speaker.name == new_name
    assert speaker.id == speaker_id
    assert speaker.team_id == team_id


@pytest.mark.asyncio
async def test_team_delete(session: AsyncSession) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(session)
    deleted_team = await delete_team(session, team_id)
    assert deleted_team == team_id

    speaker = await get_speaker(session, speaker_id)
    assert speaker is None


@pytest.mark.asyncio
async def test_speaker_delete(session: AsyncSession) -> None:
    _tournament_id, _team_id, speaker_id = await _setup_data(session)
    deleted_speaker = await delete_speaker(session, speaker_id)
    assert deleted_speaker == speaker_id

    speaker = await get_speaker(session, speaker_id)
    assert speaker is None


@pytest.mark.asyncio
async def test_speaker_list_empty(session: AsyncSession) -> None:
    speakers = await list_speakers(
        session,
        list_speakers_query=ListSpeakersQuery(),
    )
    assert speakers == []


@pytest.mark.asyncio
async def test_speaker_list(session: AsyncSession) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(session)
    speakers = await list_speakers(
        session,
        list_speakers_query=ListSpeakersQuery(),
    )
    assert len(speakers) == 1
    assert speakers[0].id == speaker_id
    assert speakers[0].team_id == team_id


@pytest.mark.asyncio
async def test_speaker_list_team_filter(session: AsyncSession) -> None:
    _first_tournament_id, first_team_id, first_speaker_id = await _setup_data(session)
    _second_tournament_id, second_team_id, second_speaker_id = await _setup_data(
        session
    )
    for team_id, speaker_id in (
        (first_team_id, first_speaker_id),
        (second_team_id, second_speaker_id),
    ):
        speakers = await list_speakers(
            session,
            list_speakers_query=ListSpeakersQuery(team_id=team_id),
        )
        assert len(speakers) == 1
        assert speakers[0].id == speaker_id
        assert speakers[0].team_id == team_id


@pytest.mark.asyncio
async def test_speaker_list_offset(session: AsyncSession) -> None:
    _tournament_id, team_id, _first_speaker_id = await _setup_data(session)
    last_speaker_id = await create_speaker(
        session,
        SpeakerCreate(name="Last", team_id=team_id),
    )
    result = await list_speakers(
        session,
        list_speakers_query=ListSpeakersQuery(offset=1),
    )
    assert len(result) == 1
    assert result[0].id == last_speaker_id
    assert result[0].name == "Last"


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
async def test_speaker_list_limit(
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
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    for idx in range(insert_n):
        _ = await create_speaker(
            session,
            SpeakerCreate(name=f"Speaker {idx}", team_id=team_id),
        )
    result = await list_speakers(
        session,
        list_speakers_query=ListSpeakersQuery(limit=limit),
    )
    assert len(result) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (
            ["Alice Smith", "Bob Smith", "Carol Jones"],
            "Smith",
            ["Alice Smith", "Bob Smith"],
        ),
        (
            ["Alice Smith", "Bob Smith", "Carol Jones"],
            "Jones",
            ["Carol Jones"],
        ),
    ],
)
@pytest.mark.asyncio
async def test_speaker_list_name_filter(
    session: AsyncSession,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    for name in insert_names:
        _ = await create_speaker(
            session,
            SpeakerCreate(name=name, team_id=team_id),
        )
    result = await list_speakers(
        session,
        list_speakers_query=ListSpeakersQuery(name=name_filter),
    )
    names = [speaker.name for speaker in result]
    assert names == expect_names


@pytest.mark.asyncio
async def test_speaker_get_missing(session: AsyncSession) -> None:
    speaker = await get_speaker(
        session,
        speaker_id=1,
    )
    assert speaker is None


@pytest.mark.asyncio
async def test_speaker_delete_missing(session: AsyncSession) -> None:
    speaker_id = await delete_speaker(
        session,
        speaker_id=1,
    )
    assert speaker_id is None


@pytest.mark.asyncio
async def test_speaker_patch_missing(session: AsyncSession) -> None:
    patch = SpeakerPatch(name="Missing")
    speaker = await patch_speaker(
        session,
        speaker_id=1,
        speaker_patch=patch,
    )
    assert speaker is None
