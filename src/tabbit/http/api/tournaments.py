from __future__ import annotations

import http
import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations import tournament as crud
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.util import not_found_response
from tabbit.schemas.tournament import ListTournamentsQuery
from tabbit.schemas.tournament import Tournament
from tabbit.schemas.tournament import TournamentCreate
from tabbit.schemas.tournament import TournamentID
from tabbit.schemas.tournament import TournamentPatch

logger = logging.getLogger(__name__)

tournaments_router = APIRouter(
    prefix="/tournaments",
    tags=[Tags.TOURNAMENT],
)


@tournaments_router.post(
    "/create",
    response_model=TournamentID,
)
async def create_tournament(
    tournament: TournamentCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a tournament.

    Returns the tournament ID upon creation.
    """
    tournament_id = TournamentID(id=await crud.create_tournament(session, tournament))
    logger.info("Created tournament.", extra={"tournament_id": tournament_id})
    return JSONResponse(content=jsonable_encoder(tournament_id))


@tournaments_router.get(
    "/{tournament_id}",
    response_model=Tournament,
    responses=not_found_response("tournament"),
)
async def get_tournament(
    tournament_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a tournament using its ID.

    Returns the tournament if found; otherwise, 404 Not Found.
    """
    tournament = await crud.get_tournament(session, tournament_id)

    if tournament is None:
        logger.info("Tournament not found.", extra={"tournament_id": tournament_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tournament not found."},
        )
    else:
        logger.info("Got tournament by ID.", extra={"tournament_id": tournament_id})
        return JSONResponse(content=jsonable_encoder(tournament))


@tournaments_router.delete(
    "/{tournament_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("tournament"),
)
async def delete_tournament(
    tournament_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing tournament.

    Returns the tournament if found; otherwise, 404 Not Found.
    """
    tournament = await crud.delete_tournament(session, tournament_id)

    if tournament is None:
        logger.info("Tournament not found.", extra={"tournament_id": tournament_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tournament not found."},
        )
    else:
        logger.info("Deleted tournament by ID.", extra={"tournament_id": tournament_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@tournaments_router.patch(
    "/{tournament_id}",
    response_model=Tournament,
    responses=not_found_response("tournament"),
)
async def patch_tournament(
    tournament_id: int,
    tournament_patch: TournamentPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing tournament.

    Returns the updated tournament.
    """
    tournament = await crud.patch_tournament(session, tournament_id, tournament_patch)

    if tournament is None:
        logger.info(
            "Tournament not found.",
            extra={"tournament_patch": tournament_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tournament not found."},
        )
    else:
        logger.info(
            "Patched tournament.",
            extra={"tournament_patch": tournament_patch},
        )
        return JSONResponse(content=jsonable_encoder(tournament))


@tournaments_router.get(
    "/",
    response_model=list[Tournament],
)
async def list_tournaments(
    query: Annotated[ListTournamentsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List tournaments with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    tournaments = await crud.list_tournaments(session, query)
    logger.info("Listed tournaments.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(tournaments))
