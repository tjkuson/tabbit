from typing import Final
from typing import Literal

from fastapi import APIRouter

root_router: Final = APIRouter(prefix="")


@root_router.get("/ping")
async def ping() -> Literal["ready"]:
    return "ready"
