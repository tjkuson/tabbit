"""HTTP API endpoints for ballot team score."""

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

from tabbit.database.operations import ballot_team_score as crud
from tabbit.database.schemas.ballot_team_score import (
    BallotTeamScoreCreate as DBBallotTeamScoreCreate,
)
from tabbit.database.schemas.ballot_team_score import (
    ListBallotTeamScoreQuery as DBListBallotTeamScoreQuery,
)
from tabbit.database.session import session_manager
from tabbit.http.api.constraint_messages import get_constraint_violation_message
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import conflict_response
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.ballot_team_score import BallotTeamScore
from tabbit.http.api.schemas.ballot_team_score import BallotTeamScoreCreate
from tabbit.http.api.schemas.ballot_team_score import BallotTeamScoreID
from tabbit.http.api.schemas.ballot_team_score import ListBallotTeamScoreQuery

logger = logging.getLogger(__name__)

ballot_team_score_router: Final = APIRouter(
    prefix="/ballot-team-score",
    tags=[Tags.BALLOT_TEAM_SCORE],
)


@ballot_team_score_router.post(
    "/create",
    response_model=BallotTeamScoreID,
    responses=conflict_response("Team score for the team in this ballot already exist"),
)
async def create_ballot_team_score(
    ballot_team_score: BallotTeamScoreCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create ballot team score.

    Returns the ballot team score ID upon creation.
    """
    db_ballot_team_score = DBBallotTeamScoreCreate(**ballot_team_score.model_dump())
    try:
        ballot_team_score_id = BallotTeamScoreID(
            id=await crud.create_ballot_team_score(session, db_ballot_team_score)
        )
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        message = get_constraint_violation_message(exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": message},
        )
    logger.info(
        "Created ballot team score.",
        extra={"ballot_team_score_id": ballot_team_score_id},
    )
    return JSONResponse(content=jsonable_encoder(ballot_team_score_id))


@ballot_team_score_router.get(
    "/{ballot_team_score_id}",
    response_model=BallotTeamScore,
    responses=not_found_response("ballot team score"),
)
async def get_ballot_team_score(
    ballot_team_score_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get ballot team score using its ID.

    Returns the ballot team score if found; otherwise, 404 Not Found.
    """
    db_ballot_team_score = await crud.get_ballot_team_score(
        session, ballot_team_score_id
    )

    if db_ballot_team_score is None:
        logger.info(
            "Ballot team score not found.",
            extra={"ballot_team_score_id": ballot_team_score_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot team score not found."},
        )
    else:
        ballot_team_score = BallotTeamScore.model_validate(db_ballot_team_score)
        logger.info(
            "Got ballot team score by ID.",
            extra={"ballot_team_score_id": ballot_team_score_id},
        )
        return JSONResponse(content=jsonable_encoder(ballot_team_score))


@ballot_team_score_router.delete(
    "/{ballot_team_score_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("ballot team score"),
)
async def delete_ballot_team_score(
    ballot_team_score_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete existing ballot team score.

    Returns the ballot team score if found; otherwise, 404 Not Found.
    """
    ballot_team_score = await crud.delete_ballot_team_score(
        session, ballot_team_score_id
    )

    if ballot_team_score is None:
        logger.info(
            "Ballot team score not found.",
            extra={"ballot_team_score_id": ballot_team_score_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Ballot team score not found."},
        )
    else:
        logger.info(
            "Deleted ballot team score by ID.",
            extra={"ballot_team_score_id": ballot_team_score_id},
        )
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@ballot_team_score_router.get(
    "/",
    response_model=list[BallotTeamScore],
)
async def list_ballot_team_score(
    query: Annotated[ListBallotTeamScoreQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List ballot team scores with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListBallotTeamScoreQuery(**query.model_dump())
    db_ballot_team_scores = await crud.list_ballot_team_score(session, db_query)
    ballot_team_scores = [
        BallotTeamScore.model_validate(db_bts) for db_bts in db_ballot_team_scores
    ]
    logger.info("Listed ballot team scores.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(ballot_team_scores))
