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

from tabbit.database.operations import debate as crud
from tabbit.database.schemas.debate import ListDebatesQuery as DBListDebatesQuery
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.debate import Debate
from tabbit.http.api.schemas.debate import DebateCreate
from tabbit.http.api.schemas.debate import DebateID
from tabbit.http.api.schemas.debate import DebatePatch
from tabbit.http.api.schemas.debate import ListDebatesQuery

logger = logging.getLogger(__name__)

debates_router: Final = APIRouter(
    prefix="/debate",
    tags=[Tags.DEBATE],
)


@debates_router.post(
    "/create",
    response_model=DebateID,
)
async def create_debate(
    debate: DebateCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a debate.

    Returns the debate ID upon creation.
    """
    debate_id = DebateID(id=await crud.create_debate(session, debate.round_id))
    logger.info("Created debate.", extra={"debate_id": debate_id})
    return JSONResponse(content=jsonable_encoder(debate_id))


@debates_router.get(
    "/{debate_id}",
    response_model=Debate,
    responses=not_found_response("debate"),
)
async def get_debate(
    debate_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a debate using its ID.

    Returns the debate if found; otherwise, 404 Not Found.
    """
    db_debate = await crud.get_debate(session, debate_id)

    if db_debate is None:
        logger.info("Debate not found.", extra={"debate_id": debate_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Debate not found."},
        )
    else:
        debate = Debate.model_validate(db_debate)
        logger.info("Got debate by ID.", extra={"debate_id": debate_id})
        return JSONResponse(content=jsonable_encoder(debate))


@debates_router.delete(
    "/{debate_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("debate"),
)
async def delete_debate(
    debate_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing debate.

    Returns the debate if found; otherwise, 404 Not Found.
    """
    debate = await crud.delete_debate(session, debate_id)

    if debate is None:
        logger.info("Debate not found.", extra={"debate_id": debate_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Debate not found."},
        )
    else:
        logger.info("Deleted debate by ID.", extra={"debate_id": debate_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@debates_router.patch(
    "/{debate_id}",
    response_model=Debate,
    responses=not_found_response("debate"),
)
async def patch_debate(
    debate_id: int,
    debate_patch: DebatePatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing debate.

    Returns the updated debate.
    """
    db_debate = await crud.patch_debate(
        session, debate_id, round_id=debate_patch.round_id
    )

    if db_debate is None:
        logger.info(
            "Debate not found.",
            extra={"debate_patch": debate_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Debate not found."},
        )
    else:
        debate = Debate.model_validate(db_debate)
        logger.info(
            "Patched debate.",
            extra={"debate_patch": debate_patch},
        )
        return JSONResponse(content=jsonable_encoder(debate))


@debates_router.get(
    "/",
    response_model=list[Debate],
)
async def list_debates(
    query: Annotated[ListDebatesQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List debates with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListDebatesQuery(**query.model_dump())
    db_debates = await crud.list_debates(session, db_query)
    debates = [Debate.model_validate(db_debate) for db_debate in db_debates]
    logger.info("Listed debates.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(debates))
