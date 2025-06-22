from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Self
from typing import final

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from tabbit.config.settings import Settings
from tabbit.config.settings import settings


@final
class SessionManager:
    """Database session manager.

    Provides a centralized way to create and manage async database
    sessions. It configures the database and session factory according
    to the provided settings.

    Attributes:
        engine: An async engine for database connections.
        sessionmaker: An async session factory for creating new database
            sessions.
    """

    def __init__(
        self,
        database_url: str,
    ) -> None:
        """Initialize a new session manager.

        Args:
            database_url: Database connection URL in SQLAlchemy format.
        """
        self.engine = create_async_engine(
            database_url,
        )
        self.sessionmaker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
    ) -> Self:
        """Create a session manager from a settings instance.

        Args:
            settings: Tabbit settings.

        Returns:
            A session manager configured in turn.
        """
        database_url = str(settings.database_url)
        return cls(database_url)

    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with self.sessionmaker() as session:
            yield session


session_manager = SessionManager.from_settings(settings)
