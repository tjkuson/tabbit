from typing import Final

from fastapi import APIRouter

from tabbit.http.api.rounds import rounds_router
from tabbit.http.api.speakers import speakers_router
from tabbit.http.api.teams import teams_router
from tabbit.http.api.tournaments import tournaments_router

api_router: Final = APIRouter(prefix="/v1")
api_router.include_router(rounds_router)
api_router.include_router(speakers_router)
api_router.include_router(teams_router)
api_router.include_router(tournaments_router)
