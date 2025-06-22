"""Database models.

This model contains the SQLAlchemy ORM models that represent the
database schema of Tabbit. Each model corresponds to a database table
and defines its columns, relationships, and behaviour.
"""

from __future__ import annotations

from typing import final

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from tabbit.database.enums import TableName


class Base(DeclarativeBase):
    """Base model for the application."""


@final
class Tournament(Base):
    __tablename__ = TableName.TOURNAMENT

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    abbreviation: Mapped[str | None]
