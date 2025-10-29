"""HTTP API endpoints for ballots."""

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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations import ballot as crud
from tabbit.database.schemas.ballot import BallotCreate as DBBallotCreate
from tabbit.database.schemas.ballot import ListBallotsQuery as DBListBallotsQuery
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import conflict_response
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.ballot import Ballot
from tabbit.http.api.schemas.ballot import BallotCreate
from tabbit.http.api.schemas.ballot import BallotID
from tabbit.http.api.schemas.ballot import ListBallotsQuery

logger = logging.getLogger(__name__)

ballots_router: Final = APIRouter(
    prefix="/ballot",
    tags=[Tags.BALLOT],
)


@ballots_router.post(
    "/create",
    response_model=BallotID,
    responses=conflict_response("Database constraint violated"),
)
async def create_ballot(
    ballot: BallotCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a ballot.

    Returns the ballot ID upon creation, or 409 Conflict if constraints are violated.
    """
    db_ballot = DBBallotCreate(**ballot.model_dump())
    try:
        ballot_id = BallotID(id=await crud.create_ballot(session, db_ballot))
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": "Database constraint violated"},
        )
    logger.info("Created ballot.", extra={"ballot_id": ballot_id})
    return JSONResponse(content=jsonable_encoder(ballot_id))


@ballots_router.get(
    "/{ballot_id}",
    response_model=Ballot,
    responses=not_found_response("ballot"),
)
async def get_ballot(
    ballot_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a ballot using its ID.

    Returns the ballot if found; otherwise, 404 Not Found.
    """
    db_ballot = await crud.get_ballot(session, ballot_id)

    if db_ballot is None:
        logger.info("Ballot not found.", extra={"ballot_id": ballot_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot not found."},
        )
    else:
        ballot = Ballot.model_validate(db_ballot)
        logger.info("Got ballot by ID.", extra={"ballot_id": ballot_id})
        return JSONResponse(content=jsonable_encoder(ballot))


@ballots_router.delete(
    "/{ballot_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("ballot"),
)
async def delete_ballot(
    ballot_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing ballot.

    Returns the ballot if found; otherwise, 404 Not Found.
    """
    ballot = await crud.delete_ballot(session, ballot_id)

    if ballot is None:
        logger.info("Ballot not found.", extra={"ballot_id": ballot_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot not found."},
        )
    else:
        logger.info("Deleted ballot by ID.", extra={"ballot_id": ballot_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@ballots_router.get(
    "/",
    response_model=list[Ballot],
)
async def list_ballots(
    query: Annotated[ListBallotsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List ballots with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListBallotsQuery(**query.model_dump())
    db_ballots = await crud.list_ballots(session, db_query)
    ballots = [Ballot.model_validate(db_ballot) for db_ballot in db_ballots]
    logger.info("Listed ballots.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(ballots))
