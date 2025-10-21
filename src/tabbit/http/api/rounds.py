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

from tabbit.database.operations import round as crud
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.util import not_found_response
from tabbit.schemas.round import ListRoundsQuery
from tabbit.schemas.round import Round
from tabbit.schemas.round import RoundCreate
from tabbit.schemas.round import RoundID
from tabbit.schemas.round import RoundPatch

logger = logging.getLogger(__name__)

rounds_router: Final = APIRouter(
    prefix="/round",
    tags=[Tags.ROUND],
)


@rounds_router.post(
    "/create",
    response_model=RoundID,
)
async def create_round(
    round_: RoundCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a round.

    Returns the round ID upon creation.
    """
    round_id = RoundID(id=await crud.create_round(session, round_))
    logger.info("Created round.", extra={"round_id": round_id})
    return JSONResponse(content=jsonable_encoder(round_id))


@rounds_router.get(
    "/{round_id}",
    response_model=Round,
    responses=not_found_response("round"),
)
async def get_round(
    round_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a round using its ID.

    Returns the round if found; otherwise, 404 Not Found.
    """
    round_ = await crud.get_round(session, round_id)

    if round_ is None:
        logger.info("Round not found.", extra={"round_id": round_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Round not found."},
        )
    else:
        logger.info("Got round by ID.", extra={"round_id": round_id})
        return JSONResponse(content=jsonable_encoder(round_))


@rounds_router.delete(
    "/{round_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("round"),
)
async def delete_round(
    round_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing round.

    Returns the round if found; otherwise, 404 Not Found.
    """
    round_ = await crud.delete_round(session, round_id)

    if round_ is None:
        logger.info("Round not found.", extra={"round_id": round_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Round not found."},
        )
    else:
        logger.info("Deleted round by ID.", extra={"round_id": round_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@rounds_router.patch(
    "/{round_id}",
    response_model=Round,
    responses=not_found_response("round"),
)
async def patch_round(
    round_id: int,
    round_patch: RoundPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing round.

    Returns the updated round.
    """
    round_ = await crud.patch_round(session, round_id, round_patch)

    if round_ is None:
        logger.info(
            "Round not found.",
            extra={"round_patch": round_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Round not found."},
        )
    else:
        logger.info(
            "Patched round.",
            extra={"round_patch": round_patch},
        )
        return JSONResponse(content=jsonable_encoder(round_))


@rounds_router.get(
    "/",
    response_model=list[Round],
)
async def list_rounds(
    query: Annotated[ListRoundsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List rounds with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    rounds = await crud.list_rounds(session, query)
    logger.info("Listed rounds.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(rounds))
