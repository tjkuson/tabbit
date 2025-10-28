import itertools
import random
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self
from typing import final

from tabbit.exceptions import TabbitComputeDrawError


@final
@dataclass(frozen=True, slots=True)
class DrawConfig:
    """Draw generation configuration."""

    teams_per_matchup: int


@final
@dataclass(frozen=True, slots=True)
class Team:
    id: int
    team_points: int
    speaker_points: int


@final
@dataclass(frozen=True, slots=True)
class Pool:
    teams: list[Team]

    def __post_init__(self) -> None:
        self.teams.sort(key=lambda team: team.team_points)

    def by_team_points(self) -> Mapping[int, list[Team]]:
        """Group the pool by team points.

        Returns:
            A map of team points to teams.
        """
        brackets = itertools.groupby(self.teams, lambda team: team.team_points)
        return {points: list(teams) for points, teams in brackets}


@final
@dataclass(frozen=True, slots=True)
class Draw:
    matchups: list[tuple[Team, ...]]

    @classmethod
    def from_pool(cls, pool: Pool, config: DrawConfig) -> Self:
        if len(pool.teams) % config.teams_per_matchup != 0:
            raise TabbitComputeDrawError(
                f"Number of teams must be a multiple of {config.teams_per_matchup}."
            )
        brackets = pool.by_team_points()
        for teams in brackets.values():
            random.shuffle(teams)
        lineup = itertools.chain.from_iterable(brackets.values())
        matchups = list(
            itertools.batched(lineup, config.teams_per_matchup, strict=True)
        )
        return cls(matchups=matchups)
