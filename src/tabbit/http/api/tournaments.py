import http
import logging
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations import tournament as crud
from tabbit.database.schemas import tournament as db_schemas
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.tournament import ListTournamentsQuery
from tabbit.http.api.schemas.tournament import Tournament
from tabbit.http.api.schemas.tournament import TournamentCreate
from tabbit.http.api.schemas.tournament import TournamentID
from tabbit.http.api.schemas.tournament import TournamentPatch

logger = logging.getLogger(__name__)

tournaments_router: Final = APIRouter(
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
    db_tournament = db_schemas.TournamentCreate(**tournament.model_dump())
    tournament_id = TournamentID(
        id=await crud.create_tournament(session, db_tournament)
    )
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
    db_tournament = await crud.get_tournament(session, tournament_id)

    if db_tournament is None:
        logger.info("Tournament not found.", extra={"tournament_id": tournament_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tournament not found."},
        )
    else:
        tournament = Tournament.model_validate(db_tournament)
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
    patch_data = tournament_patch.model_dump(exclude_unset=True)
    db_patch = db_schemas.TournamentPatch(**patch_data)
    db_tournament = await crud.patch_tournament(session, tournament_id, db_patch)

    if db_tournament is None:
        logger.info(
            "Tournament not found.",
            extra={"tournament_patch": tournament_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tournament not found."},
        )
    else:
        tournament = Tournament.model_validate(db_tournament)
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
    db_query = db_schemas.ListTournamentsQuery(**query.model_dump())
    db_tournaments = await crud.list_tournaments(session, db_query)
    tournaments = [
        Tournament.model_validate(db_tournament) for db_tournament in db_tournaments
    ]
    logger.info("Listed tournaments.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(tournaments))
