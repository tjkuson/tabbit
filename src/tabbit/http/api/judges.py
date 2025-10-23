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

from tabbit.database.operations import judge as crud
from tabbit.database.schemas.judge import JudgeCreate as DBJudgeCreate
from tabbit.database.schemas.judge import ListJudgesQuery as DBListJudgesQuery
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.schemas.judge import Judge
from tabbit.http.api.schemas.judge import JudgeCreate
from tabbit.http.api.schemas.judge import JudgeID
from tabbit.http.api.schemas.judge import JudgePatch
from tabbit.http.api.schemas.judge import ListJudgesQuery
from tabbit.http.api.util import not_found_response

logger = logging.getLogger(__name__)

judges_router: Final = APIRouter(
    prefix="/judge",
    tags=[Tags.JUDGE],
)


@judges_router.post(
    "/create",
    response_model=JudgeID,
)
async def create_judge(
    judge: JudgeCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a judge.

    Returns the judge ID upon creation.
    """
    db_judge = DBJudgeCreate(**judge.model_dump())
    judge_id = JudgeID(id=await crud.create_judge(session, db_judge))
    logger.info("Created judge.", extra={"judge_id": judge_id})
    return JSONResponse(content=jsonable_encoder(judge_id))


@judges_router.get(
    "/{judge_id}",
    response_model=Judge,
    responses=not_found_response("judge"),
)
async def get_judge(
    judge_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a judge using its ID.

    Returns the judge if found; otherwise, 404 Not Found.
    """
    db_judge = await crud.get_judge(session, judge_id)

    if db_judge is None:
        logger.info("Judge not found.", extra={"judge_id": judge_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Judge not found."},
        )
    else:
        judge = Judge.model_validate(db_judge)
        logger.info("Got judge by ID.", extra={"judge_id": judge_id})
        return JSONResponse(content=jsonable_encoder(judge))


@judges_router.delete(
    "/{judge_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("judge"),
)
async def delete_judge(
    judge_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing judge.

    Returns the judge if found; otherwise, 404 Not Found.
    """
    judge = await crud.delete_judge(session, judge_id)

    if judge is None:
        logger.info("Judge not found.", extra={"judge_id": judge_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Judge not found."},
        )
    else:
        logger.info("Deleted judge by ID.", extra={"judge_id": judge_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@judges_router.patch(
    "/{judge_id}",
    response_model=Judge,
    responses=not_found_response("judge"),
)
async def patch_judge(
    judge_id: int,
    judge_patch: JudgePatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing judge.

    Returns the updated judge.
    """
    db_judge = await crud.patch_judge(session, judge_id, name=judge_patch.name)

    if db_judge is None:
        logger.info(
            "Judge not found.",
            extra={"judge_patch": judge_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Judge not found."},
        )
    else:
        judge = Judge.model_validate(db_judge)
        logger.info(
            "Patched judge.",
            extra={"judge_patch": judge_patch},
        )
        return JSONResponse(content=jsonable_encoder(judge))


@judges_router.get(
    "/",
    response_model=list[Judge],
)
async def list_judges(
    query: Annotated[ListJudgesQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List judges with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListJudgesQuery(**query.model_dump())
    db_judges = await crud.list_judges(session, db_query)
    judges = [Judge.model_validate(db_judge) for db_judge in db_judges]
    logger.info("Listed judges.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(judges))
