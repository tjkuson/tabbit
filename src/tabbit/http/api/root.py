from __future__ import annotations

from fastapi import APIRouter

from tabbit.http.api.teams import teams_router
from tabbit.http.api.tournaments import tournaments_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(teams_router)
api_router.include_router(tournaments_router)
