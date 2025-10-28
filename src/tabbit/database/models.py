"""Database models.

This model contains the SQLAlchemy ORM models that represent the
database schema of Tabbit. Each model corresponds to a database table
and defines its columns, relationships, and behaviour.
"""

from typing import final

from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from tabbit.database.enums import RoundStatus
from tabbit.database.enums import TableName


class Base(DeclarativeBase):
    """Base model for the application."""


@final
class Tournament(Base):
    __tablename__ = TableName.TOURNAMENT

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    abbreviation: Mapped[str | None]

    judges: Mapped[list[Judge]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
    teams: Mapped[list[Team]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
    rounds: Mapped[list[Round]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )


@final
class Team(Base):
    __tablename__ = TableName.TEAM
    __table_args__ = (
        UniqueConstraint("tournament_id", "name", name="uq_team_tournament_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TOURNAMENT}.id"))
    name: Mapped[str]
    abbreviation: Mapped[str | None]

    tournament: Mapped[Tournament] = relationship(back_populates="teams")
    speakers: Mapped[list[Speaker]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )


@final
class Speaker(Base):
    __tablename__ = TableName.SPEAKER

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TEAM}.id"))
    name: Mapped[str]

    team: Mapped[Team] = relationship(back_populates="speakers")
    ballot_speaker_points: Mapped[list[BallotSpeakerPoints]] = relationship(
        back_populates="speaker",
        cascade="all, delete-orphan",
    )


@final
class Judge(Base):
    __tablename__ = TableName.JUDGE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TOURNAMENT}.id"))
    name: Mapped[str]

    tournament: Mapped[Tournament] = relationship(back_populates="judges")
    ballots: Mapped[list[Ballot]] = relationship(
        back_populates="judge",
        cascade="all, delete-orphan",
    )


@final
class Round(Base):
    __tablename__ = TableName.ROUND
    __table_args__ = (
        UniqueConstraint(
            "tournament_id", "sequence", name="uq_round_tournament_sequence"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TOURNAMENT}.id"))
    name: Mapped[str]
    abbreviation: Mapped[str | None]
    sequence: Mapped[int]
    status: Mapped[RoundStatus]

    tournament: Mapped[Tournament] = relationship(back_populates="rounds")
    debates: Mapped[list[Debate]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan",
    )
    motions: Mapped[list[Motion]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan",
    )


@final
class Motion(Base):
    __tablename__ = TableName.MOTION

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.ROUND}.id"))
    text: Mapped[str]
    infoslide: Mapped[str | None]

    round: Mapped[Round] = relationship(back_populates="motions")


@final
class Debate(Base):
    __tablename__ = TableName.DEBATE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.ROUND}.id"))

    round: Mapped[Round] = relationship(back_populates="debates")
    ballots: Mapped[list[Ballot]] = relationship(
        back_populates="debate",
        cascade="all, delete-orphan",
    )


@final
class Ballot(Base):
    __tablename__ = TableName.BALLOT

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    debate_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.DEBATE}.id"))
    judge_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.JUDGE}.id"))
    version: Mapped[int] = mapped_column(default=1)

    debate: Mapped[Debate] = relationship(back_populates="ballots")
    judge: Mapped[Judge] = relationship(back_populates="ballots")
    ballot_speaker_points: Mapped[list[BallotSpeakerPoints]] = relationship(
        back_populates="ballot",
        cascade="all, delete-orphan",
    )
    ballot_team_scores: Mapped[list[BallotTeamScore]] = relationship(
        back_populates="ballot",
        cascade="all, delete-orphan",
    )


@final
class BallotSpeakerPoints(Base):
    __tablename__ = TableName.BALLOT_SPEAKER_POINTS
    __table_args__ = (
        UniqueConstraint("ballot_id", "speaker_id", name="uq_ballot_speaker"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ballot_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.BALLOT}.id"))
    speaker_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.SPEAKER}.id"))
    speaker_position: Mapped[int]
    score: Mapped[int]

    ballot: Mapped[Ballot] = relationship(back_populates="ballot_speaker_points")
    speaker: Mapped[Speaker] = relationship(back_populates="ballot_speaker_points")


@final
class BallotTeamScore(Base):
    __tablename__ = TableName.BALLOT_TEAM_SCORE
    __table_args__ = (UniqueConstraint("ballot_id", "team_id", name="uq_ballot_team"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ballot_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.BALLOT}.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TEAM}.id"))
    score: Mapped[int]

    ballot: Mapped[Ballot] = relationship(back_populates="ballot_team_scores")
    team: Mapped[Team] = relationship()
