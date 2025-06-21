from __future__ import annotations

from typing import Literal

from fastapi import APIRouter

root_router = APIRouter(prefix="")


@root_router.get("/ping")
async def ping() -> Literal["ready"]:
    return "ready"
