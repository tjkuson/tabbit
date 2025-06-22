from __future__ import annotations

from pathlib import Path
from typing import final

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="tabbit_", env_file=".env")

    database_url: str = "sqlite+aiosqlite:///tabbit.db"
    log_filename: Path = Path("tabbit.log.jsonl")


settings = Settings()
