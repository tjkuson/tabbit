"""HTTP API endpoints for ballot speaker points."""

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

from tabbit.database.operations import ballot_speaker_points as crud
from tabbit.database.schemas.ballot_speaker_points import (
    BallotSpeakerPointsCreate as DBBallotSpeakerPointsCreate,
)
from tabbit.database.schemas.ballot_speaker_points import (
    ListBallotSpeakerPointsQuery as DBListBallotSpeakerPointsQuery,
)
from tabbit.database.session import session_manager
from tabbit.http.api.constraint_messages import get_constraint_violation_message
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import conflict_response
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.ballot_speaker_points import BallotSpeakerPoints
from tabbit.http.api.schemas.ballot_speaker_points import BallotSpeakerPointsCreate
from tabbit.http.api.schemas.ballot_speaker_points import BallotSpeakerPointsID
from tabbit.http.api.schemas.ballot_speaker_points import ListBallotSpeakerPointsQuery

logger = logging.getLogger(__name__)

ballot_speaker_points_router: Final = APIRouter(
    prefix="/ballot-speaker-points",
    tags=[Tags.BALLOT_SPEAKER_POINTS],
)


@ballot_speaker_points_router.post(
    "/create",
    response_model=BallotSpeakerPointsID,
    responses=conflict_response(
        "Speaker points for the speaker in this ballot already exist"
    ),
)
async def create_ballot_speaker_points(
    ballot_speaker_points: BallotSpeakerPointsCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create ballot speaker points.

    Returns the ballot speaker points ID upon creation.
    """
    db_ballot_speaker_points = DBBallotSpeakerPointsCreate(
        **ballot_speaker_points.model_dump()
    )
    try:
        ballot_speaker_points_id = BallotSpeakerPointsID(
            id=await crud.create_ballot_speaker_points(
                session, db_ballot_speaker_points
            )
        )
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        message = get_constraint_violation_message(exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": message},
        )
    logger.info(
        "Created ballot speaker points.",
        extra={"ballot_speaker_points_id": ballot_speaker_points_id},
    )
    return JSONResponse(content=jsonable_encoder(ballot_speaker_points_id))


@ballot_speaker_points_router.get(
    "/{ballot_speaker_points_id}",
    response_model=BallotSpeakerPoints,
    responses=not_found_response("ballot speaker points"),
)
async def get_ballot_speaker_points(
    ballot_speaker_points_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get ballot speaker points using its ID.

    Returns the ballot speaker points if found; otherwise, 404 Not Found.
    """
    db_ballot_speaker_points = await crud.get_ballot_speaker_points(
        session, ballot_speaker_points_id
    )

    if db_ballot_speaker_points is None:
        logger.info(
            "Ballot speaker points not found.",
            extra={"ballot_speaker_points_id": ballot_speaker_points_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot speaker points not found."},
        )
    else:
        ballot_speaker_points = BallotSpeakerPoints.model_validate(
            db_ballot_speaker_points
        )
        logger.info(
            "Got ballot speaker points by ID.",
            extra={"ballot_speaker_points_id": ballot_speaker_points_id},
        )
        return JSONResponse(content=jsonable_encoder(ballot_speaker_points))


@ballot_speaker_points_router.delete(
    "/{ballot_speaker_points_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("ballot speaker points"),
)
async def delete_ballot_speaker_points(
    ballot_speaker_points_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete existing ballot speaker points.

    Returns the ballot speaker points if found; otherwise, 404 Not Found.
    """
    ballot_speaker_points = await crud.delete_ballot_speaker_points(
        session, ballot_speaker_points_id
    )

    if ballot_speaker_points is None:
        logger.info(
            "Ballot speaker points not found.",
            extra={"ballot_speaker_points_id": ballot_speaker_points_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot speaker points not found."},
        )
    else:
        logger.info(
            "Deleted ballot speaker points by ID.",
            extra={"ballot_speaker_points_id": ballot_speaker_points_id},
        )
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@ballot_speaker_points_router.get(
    "/",
    response_model=list[BallotSpeakerPoints],
)
async def list_ballot_speaker_points(
    query: Annotated[ListBallotSpeakerPointsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List ballot speaker points with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListBallotSpeakerPointsQuery(**query.model_dump())
    db_ballot_speaker_points = await crud.list_ballot_speaker_points(session, db_query)
    ballot_speaker_points = [
        BallotSpeakerPoints.model_validate(db_bsp)
        for db_bsp in db_ballot_speaker_points
    ]
    logger.info("Listed ballot speaker points.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(ballot_speaker_points))
