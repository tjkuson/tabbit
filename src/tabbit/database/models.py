"""Database models.

This model contains the SQLAlchemy ORM models that represent the
database schema of Tabbit. Each model corresponds to a database table
and defines its columns, relationships, and behaviour.
"""

from __future__ import annotations

from typing import final

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from tabbit.database.enums import TableName


class Base(DeclarativeBase):
    """Base model for the application."""


@final
class Tournament(Base):
    __tablename__ = TableName.TOURNAMENT

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    abbreviation: Mapped[str | None]

    teams: Mapped[list[Team]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )


@final
class Team(Base):
    __tablename__ = TableName.TEAM

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey(f"{TableName.TOURNAMENT}.id"))
    name: Mapped[str]
    abbreviation: Mapped[str | None]

    tournament: Mapped[Tournament] = relationship(back_populates="teams")
