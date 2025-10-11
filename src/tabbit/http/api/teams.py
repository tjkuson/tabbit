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

from tabbit.database.operations import team as crud
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.util import not_found_response
from tabbit.schemas.team import ListTeamsQuery
from tabbit.schemas.team import Team
from tabbit.schemas.team import TeamCreate
from tabbit.schemas.team import TeamID
from tabbit.schemas.team import TeamPatch

logger = logging.getLogger(__name__)

teams_router = APIRouter(
    prefix="/team",
    tags=[Tags.TEAM],
)


@teams_router.post(
    "/create",
    response_model=TeamID,
)
async def create_team(
    team: TeamCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a team.

    Returns the team ID upon creation.
    """
    team_id = TeamID(id=await crud.create_team(session, team))
    logger.info("Created team.", extra={"team_id": team_id})
    return JSONResponse(content=jsonable_encoder(team_id))


@teams_router.get(
    "/{team_id}",
    response_model=Team,
    responses=not_found_response("team"),
)
async def get_team(
    team_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a team using its ID.

    Returns the team if found; otherwise, 404 Not Found.
    """
    team = await crud.get_team(session, team_id)

    if team is None:
        logger.info("Team not found.", extra={"team_id": team_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Team not found."},
        )
    else:
        logger.info("Got team by ID.", extra={"team_id": team_id})
        return JSONResponse(content=jsonable_encoder(team))


@teams_router.delete(
    "/{team_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("team"),
)
async def delete_team(
    team_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing team.

    Returns the team if found; otherwise, 404 Not Found.
    """
    team = await crud.delete_team(session, team_id)

    if team is None:
        logger.info("Team not found.", extra={"team_id": team_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Team not found."},
        )
    else:
        logger.info("Deleted team by ID.", extra={"team_id": team_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@teams_router.patch(
    "/{team_id}",
    response_model=Team,
    responses=not_found_response("team"),
)
async def patch_team(
    team_id: int,
    team_patch: TeamPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing team.

    Returns the updated team.
    """
    team = await crud.patch_team(session, team_id, team_patch)

    if team is None:
        logger.info(
            "Team not found.",
            extra={"team_patch": team_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Team not found."},
        )
    else:
        logger.info(
            "Patched team.",
            extra={"team_patch": team_patch},
        )
        return JSONResponse(content=jsonable_encoder(team))


@teams_router.get(
    "/",
    response_model=list[Team],
)
async def list_teams(
    query: Annotated[ListTeamsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List teams with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    teams = await crud.list_teams(session, query)
    logger.info("Listed teams.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(teams))
