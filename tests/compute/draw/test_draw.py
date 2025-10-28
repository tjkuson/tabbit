from collections.abc import Mapping

import pytest

from tabbit.compute.draw import Draw
from tabbit.compute.draw import DrawConfig
from tabbit.compute.draw import Pool
from tabbit.compute.draw import Team
from tabbit.exceptions import TabbitComputeDrawError


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        (
            Pool(teams=[]),
            {},
        ),
        (
            Pool(
                teams=[
                    Team(id=1, team_points=1, speaker_points=1),
                ]
            ),
            {
                1: [
                    Team(id=1, team_points=1, speaker_points=1),
                ],
            },
        ),
        (
            Pool(
                teams=[
                    Team(id=1, team_points=1, speaker_points=1),
                    Team(id=2, team_points=1, speaker_points=1),
                ]
            ),
            {
                1: [
                    Team(id=1, team_points=1, speaker_points=1),
                    Team(id=2, team_points=1, speaker_points=1),
                ],
            },
        ),
        (
            Pool(
                teams=[
                    Team(id=1, team_points=1, speaker_points=1),
                    Team(id=2, team_points=2, speaker_points=1),
                ]
            ),
            {
                1: [
                    Team(id=1, team_points=1, speaker_points=1),
                ],
                2: [
                    Team(id=2, team_points=2, speaker_points=1),
                ],
            },
        ),
        (
            Pool(
                teams=[
                    Team(id=2, team_points=2, speaker_points=1),
                    Team(id=1, team_points=1, speaker_points=1),
                ]
            ),
            {
                1: [
                    Team(id=1, team_points=1, speaker_points=1),
                ],
                2: [
                    Team(id=2, team_points=2, speaker_points=1),
                ],
            },
        ),
    ],
)
def test_pool_by_team_points(
    pool: Pool,
    expected: Mapping[int, list[Team]],
) -> None:
    assert pool.by_team_points() == expected


@pytest.mark.parametrize(
    ("pool", "config"),
    [
        (
            Pool(teams=[Team(id=1, team_points=0, speaker_points=0)]),
            DrawConfig(teams_per_matchup=2),
        ),
        (
            Pool(
                teams=[
                    Team(id=1, team_points=0, speaker_points=0),
                    Team(id=2, team_points=0, speaker_points=0),
                    Team(id=3, team_points=0, speaker_points=0),
                ]
            ),
            DrawConfig(teams_per_matchup=2),
        ),
        (
            Pool(
                teams=[
                    Team(id=1, team_points=0, speaker_points=0),
                    Team(id=2, team_points=0, speaker_points=0),
                    Team(id=3, team_points=0, speaker_points=0),
                    Team(id=4, team_points=0, speaker_points=0),
                    Team(id=5, team_points=0, speaker_points=0),
                ]
            ),
            DrawConfig(teams_per_matchup=4),
        ),
    ],
)
def test_draw_from_pool_invalid_team_count(
    pool: Pool,
    config: DrawConfig,
) -> None:
    with pytest.raises(
        TabbitComputeDrawError,
        match=f"Number of teams must be a multiple of {config.teams_per_matchup}",
    ):
        Draw.from_pool(pool, config)


def test_draw_from_pool_empty() -> None:
    pool = Pool(teams=[])
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)
    assert len(draw.matchups) == 0


def test_draw_from_pool_single_matchup() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=0, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 1
    assert len(draw.matchups[0]) == 2
    team_ids = {team.id for team in draw.matchups[0]}
    assert team_ids == {1, 2}


def test_draw_from_pool_multiple_matchups_same_bracket() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=0, speaker_points=0),
            Team(id=3, team_points=0, speaker_points=0),
            Team(id=4, team_points=0, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 2
    assert len(draw.matchups[0]) == 2
    assert len(draw.matchups[1]) == 2

    all_team_ids = {team.id for matchup in draw.matchups for team in matchup}
    assert all_team_ids == {1, 2, 3, 4}


def test_draw_from_pool_multiple_brackets_no_pullup() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=1, speaker_points=0),
            Team(id=2, team_points=1, speaker_points=0),
            Team(id=3, team_points=2, speaker_points=0),
            Team(id=4, team_points=2, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 2

    all_teams = [team for matchup in draw.matchups for team in matchup]
    team_ids = [team.id for team in all_teams]
    team_points = [team.team_points for team in all_teams]

    assert set(team_ids) == {1, 2, 3, 4}

    assert team_points[0] == 1
    assert team_points[1] == 1
    assert team_points[2] == 2
    assert team_points[3] == 2


def test_draw_from_pool_two_vs_two() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=0, speaker_points=0),
            Team(id=3, team_points=0, speaker_points=0),
            Team(id=4, team_points=0, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=4)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 1
    assert len(draw.matchups[0]) == 4
    team_ids = {team.id for team in draw.matchups[0]}
    assert team_ids == {1, 2, 3, 4}


def test_draw_from_pool_simple_pullup() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=0, speaker_points=0),
            Team(id=3, team_points=0, speaker_points=0),
            Team(id=4, team_points=1, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 2

    all_team_ids = [team.id for matchup in draw.matchups for team in matchup]
    assert sorted(all_team_ids) == [1, 2, 3, 4]

    all_teams = [team for matchup in draw.matchups for team in matchup]
    team_points = [team.team_points for team in all_teams]

    assert team_points[0] == 0
    assert team_points[1] == 0
    assert team_points[2] == 0
    assert team_points[3] == 1


def test_draw_from_pool_multi_bracket_pullup() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=1, speaker_points=0),
            Team(id=3, team_points=2, speaker_points=0),
            Team(id=4, team_points=2, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=4)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 1
    assert len(draw.matchups[0]) == 4

    all_team_ids = {team.id for team in draw.matchups[0]}
    assert all_team_ids == {1, 2, 3, 4}

    teams_in_matchup = draw.matchups[0]
    team_points = [team.team_points for team in teams_in_matchup]

    assert team_points[0] == 0
    assert team_points[1] == 1
    assert team_points[2] == 2
    assert team_points[3] == 2


def test_draw_from_pool_pullup_in_two_vs_two() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=0, speaker_points=0),
            Team(id=3, team_points=0, speaker_points=0),
            Team(id=4, team_points=0, speaker_points=0),
            Team(id=5, team_points=0, speaker_points=0),
            Team(id=6, team_points=0, speaker_points=0),
            Team(id=7, team_points=1, speaker_points=0),
            Team(id=8, team_points=1, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=4)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 2

    all_team_ids = [team.id for matchup in draw.matchups for team in matchup]
    assert sorted(all_team_ids) == [1, 2, 3, 4, 5, 6, 7, 8]

    for matchup in draw.matchups:
        assert len(matchup) == 4

    all_teams = [team for matchup in draw.matchups for team in matchup]
    team_points = [team.team_points for team in all_teams]

    assert team_points[0] == 0
    assert team_points[1] == 0
    assert team_points[2] == 0
    assert team_points[3] == 0
    assert team_points[4] == 0
    assert team_points[5] == 0
    assert team_points[6] == 1
    assert team_points[7] == 1


def test_draw_from_pool_multiple_pullups() -> None:
    pool = Pool(
        teams=[
            Team(id=1, team_points=0, speaker_points=0),
            Team(id=2, team_points=1, speaker_points=0),
            Team(id=3, team_points=1, speaker_points=0),
            Team(id=4, team_points=2, speaker_points=0),
            Team(id=5, team_points=2, speaker_points=0),
            Team(id=6, team_points=3, speaker_points=0),
        ]
    )
    config = DrawConfig(teams_per_matchup=2)
    draw = Draw.from_pool(pool, config)

    assert len(draw.matchups) == 3

    all_team_ids = [team.id for matchup in draw.matchups for team in matchup]
    assert sorted(all_team_ids) == [1, 2, 3, 4, 5, 6]

    for matchup in draw.matchups:
        assert len(matchup) == 2

    all_teams = [team for matchup in draw.matchups for team in matchup]
    team_points = [team.team_points for team in all_teams]

    assert team_points[0] == 0
    assert team_points[1] == 1
    assert team_points[2] == 1
    assert team_points[3] == 2
    assert team_points[4] == 2
    assert team_points[5] == 3
