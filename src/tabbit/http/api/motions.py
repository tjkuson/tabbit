"""HTTP API endpoints for motions."""

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

from tabbit.database.operations import motion as crud
from tabbit.database.schemas import motion as db_schemas
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.motion import ListMotionsQuery
from tabbit.http.api.schemas.motion import Motion
from tabbit.http.api.schemas.motion import MotionCreate
from tabbit.http.api.schemas.motion import MotionID
from tabbit.http.api.schemas.motion import MotionPatch

logger = logging.getLogger(__name__)

motions_router: Final = APIRouter(
    prefix="/motion",
    tags=[Tags.MOTION],
)


@motions_router.post(
    "/create",
    response_model=MotionID,
)
async def create_motion(
    motion: MotionCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a motion.

    Returns the motion ID upon creation.
    """
    db_motion = db_schemas.MotionCreate(**motion.model_dump())
    motion_id = MotionID(id=await crud.create_motion(session, db_motion))
    logger.info("Created motion.", extra={"motion_id": motion_id})
    return JSONResponse(content=jsonable_encoder(motion_id))


@motions_router.get(
    "/{motion_id}",
    response_model=Motion,
    responses=not_found_response("motion"),
)
async def get_motion(
    motion_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a motion using its ID.

    Returns the motion if found; otherwise, 404 Not Found.
    """
    db_motion = await crud.get_motion(session, motion_id)

    if db_motion is None:
        logger.info("Motion not found.", extra={"motion_id": motion_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Motion not found."},
        )
    else:
        motion = Motion.model_validate(db_motion)
        logger.info("Got motion by ID.", extra={"motion_id": motion_id})
        return JSONResponse(content=jsonable_encoder(motion))


@motions_router.delete(
    "/{motion_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("motion"),
)
async def delete_motion(
    motion_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing motion.

    Returns 204 No Content if successful; otherwise, 404 Not Found.
    """
    motion = await crud.delete_motion(session, motion_id)

    if motion is None:
        logger.info("Motion not found.", extra={"motion_id": motion_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Motion not found."},
        )
    else:
        logger.info("Deleted motion by ID.", extra={"motion_id": motion_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@motions_router.patch(
    "/{motion_id}",
    response_model=Motion,
    responses=not_found_response("motion"),
)
async def patch_motion(
    motion_id: int,
    motion_patch: MotionPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing motion.

    Returns the updated motion.
    """
    patch_data = motion_patch.model_dump(exclude_unset=True)
    db_patch = db_schemas.MotionPatch(**patch_data)
    db_motion = await crud.patch_motion(session, motion_id, db_patch)

    if db_motion is None:
        logger.info(
            "Motion not found.",
            extra={"motion_patch": motion_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Motion not found."},
        )
    else:
        motion = Motion.model_validate(db_motion)
        logger.info(
            "Patched motion.",
            extra={"motion_patch": motion_patch},
        )
        return JSONResponse(content=jsonable_encoder(motion))


@motions_router.get(
    "/",
    response_model=list[Motion],
)
async def list_motions(
    query: Annotated[ListMotionsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List motions with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = db_schemas.ListMotionsQuery(**query.model_dump())
    db_motions = await crud.list_motions(session, db_query)
    motions = [Motion.model_validate(db_motion) for db_motion in db_motions]
    logger.info("Listed motions.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(motions))
