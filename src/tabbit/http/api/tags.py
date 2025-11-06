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

from tabbit.database.operations import tag as crud
from tabbit.database.schemas import tag as db_schemas
from tabbit.database.session import session_manager
from tabbit.http.api.constraint_messages import get_constraint_violation_message
from tabbit.http.api.enums import Tags
from tabbit.http.api.responses import conflict_response
from tabbit.http.api.responses import not_found_response
from tabbit.http.api.schemas.judge import Judge
from tabbit.http.api.schemas.speaker import Speaker
from tabbit.http.api.schemas.tag import AddJudgesToTag
from tabbit.http.api.schemas.tag import AddSpeakersToTag
from tabbit.http.api.schemas.tag import ListTagsQuery
from tabbit.http.api.schemas.tag import Tag
from tabbit.http.api.schemas.tag import TagCreate
from tabbit.http.api.schemas.tag import TagID
from tabbit.http.api.schemas.tag import TagPatch

logger = logging.getLogger(__name__)

tags_router: Final = APIRouter(
    prefix="/tag",
    tags=[Tags.TAG],
)


@tags_router.post(
    "/create",
    response_model=TagID,
    responses=conflict_response("Database constraint violated"),
)
async def create_tag(
    tag: TagCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a tag.

    Returns the tag ID upon creation, or 409 Conflict if constraints are
    violated.
    """
    db_tag = db_schemas.TagCreate(**tag.model_dump())
    try:
        tag_id = TagID(id=await crud.create_tag(session, db_tag))
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        msg = get_constraint_violation_message(exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": msg},
        )
    logger.info("Created tag.", extra={"tag_id": tag_id})
    return JSONResponse(content=jsonable_encoder(tag_id))


@tags_router.get(
    "/{tag_id}",
    response_model=Tag,
    responses=not_found_response("tag"),
)
async def get_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a tag using its ID.

    Returns the tag if found; otherwise, 404 Not Found.
    """
    db_tag = await crud.get_tag(session, tag_id)

    if db_tag is None:
        logger.info("Tag not found.", extra={"tag_id": tag_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tag not found."},
        )
    else:
        tag = Tag.model_validate(db_tag)
        logger.info("Got tag by ID.", extra={"tag_id": tag_id})
        return JSONResponse(content=jsonable_encoder(tag))


@tags_router.delete(
    "/{tag_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("tag"),
)
async def delete_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing tag.

    Returns 204 No Content if successful; otherwise, 404 Not Found.
    """
    tag = await crud.delete_tag(session, tag_id)

    if tag is None:
        logger.info("Tag not found.", extra={"tag_id": tag_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tag not found."},
        )
    else:
        logger.info("Deleted tag by ID.", extra={"tag_id": tag_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@tags_router.patch(
    "/{tag_id}",
    response_model=Tag,
    responses=not_found_response("tag"),
)
async def patch_tag(
    tag_id: int,
    tag_patch: TagPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing tag.

    Returns the updated tag.
    """
    patch_data = tag_patch.model_dump(exclude_unset=True)
    db_patch = db_schemas.TagPatch(**patch_data)
    db_tag = await crud.patch_tag(session, tag_id, db_patch)

    if db_tag is None:
        logger.info(
            "Tag not found.",
            extra={"tag_patch": tag_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tag not found."},
        )
    else:
        tag = Tag.model_validate(db_tag)
        logger.info(
            "Patched tag.",
            extra={"tag_patch": tag_patch},
        )
        return JSONResponse(content=jsonable_encoder(tag))


@tags_router.get(
    "/",
    response_model=list[Tag],
)
async def list_tags(
    query: Annotated[ListTagsQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List tags with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = db_schemas.ListTagsQuery(**query.model_dump())
    db_tags = await crud.list_tags(session, db_query)
    tags = [Tag.model_validate(db_tag) for db_tag in db_tags]
    logger.info("Listed tags.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(tags))


@tags_router.post(
    "/{tag_id}/speakers",
    response_model=TagID,
    responses=conflict_response("Database constraint violated")
    | not_found_response("tag"),
)
async def add_speakers_to_tag(
    tag_id: int,
    add_speakers: AddSpeakersToTag,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Add speakers to a tag.

    Returns the tag ID if successful, 404 if tag not found, or 409 on
    constraint violation.
    """
    try:
        result = await crud.add_speakers_to_tag(
            session, tag_id, add_speakers.speaker_ids
        )
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        msg = get_constraint_violation_message(exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": msg},
        )

    if result is None:
        logger.info("Tag not found.", extra={"tag_id": tag_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tag not found."},
        )
    else:
        logger.info(
            "Added speakers to tag.",
            extra={"tag_id": tag_id, "speaker_ids": add_speakers.speaker_ids},
        )
        return JSONResponse(content=jsonable_encoder(TagID(id=result)))


@tags_router.delete(
    "/{tag_id}/speakers/{speaker_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("speaker-tag association"),
)
async def remove_speaker_from_tag(
    tag_id: int,
    speaker_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Remove a speaker from a tag.

    Returns 204 No Content if successful; otherwise, 404 Not Found.
    """
    result = await crud.remove_speaker_from_tag(session, tag_id, speaker_id)

    if result is None:
        logger.info(
            "Speaker-tag association not found.",
            extra={"tag_id": tag_id, "speaker_id": speaker_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Speaker-tag association not found."},
        )
    else:
        logger.info(
            "Removed speaker from tag.",
            extra={"tag_id": tag_id, "speaker_id": speaker_id},
        )
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@tags_router.get(
    "/{tag_id}/speakers",
    response_model=list[Speaker],
)
async def list_speakers_for_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List speakers associated with a tag.

    Returns an empty list if none are found.
    """
    db_speakers = await crud.list_speakers_for_tag(session, tag_id)
    speakers = [Speaker.model_validate(db_speaker) for db_speaker in db_speakers]
    logger.info("Listed speakers for tag.", extra={"tag_id": tag_id})
    return JSONResponse(content=jsonable_encoder(speakers))


@tags_router.post(
    "/{tag_id}/judges",
    response_model=TagID,
    responses=conflict_response("Database constraint violated")
    | not_found_response("tag"),
)
async def add_judges_to_tag(
    tag_id: int,
    add_judges: AddJudgesToTag,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Add judges to a tag.

    Returns the tag ID if successful, 404 if tag not found, or 409 on
    constraint violation.
    """
    try:
        result = await crud.add_judges_to_tag(session, tag_id, add_judges.judge_ids)
    except IntegrityError as exc:
        logger.warning("Constraint violation.", exc_info=exc)
        msg = get_constraint_violation_message(exc)
        return JSONResponse(
            status_code=http.HTTPStatus.CONFLICT,
            content={"message": msg},
        )

    if result is None:
        logger.info("Tag not found.", extra={"tag_id": tag_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Tag not found."},
        )
    else:
        logger.info(
            "Added judges to tag.",
            extra={"tag_id": tag_id, "judge_ids": add_judges.judge_ids},
        )
        return JSONResponse(content=jsonable_encoder(TagID(id=result)))


@tags_router.delete(
    "/{tag_id}/judges/{judge_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("judge-tag association"),
)
async def remove_judge_from_tag(
    tag_id: int,
    judge_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Remove a judge from a tag.

    Returns 204 No Content if successful; otherwise, 404 Not Found.
    """
    result = await crud.remove_judge_from_tag(session, tag_id, judge_id)

    if result is None:
        logger.info(
            "Judge-tag association not found.",
            extra={"tag_id": tag_id, "judge_id": judge_id},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Judge-tag association not found."},
        )
    else:
        logger.info(
            "Removed judge from tag.",
            extra={"tag_id": tag_id, "judge_id": judge_id},
        )
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@tags_router.get(
    "/{tag_id}/judges",
    response_model=list[Judge],
)
async def list_judges_for_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List judges associated with a tag.

    Returns an empty list if none are found.
    """
    db_judges = await crud.list_judges_for_tag(session, tag_id)
    judges = [Judge.model_validate(db_judge) for db_judge in db_judges]
    logger.info("Listed judges for tag.", extra={"tag_id": tag_id})
    return JSONResponse(content=jsonable_encoder(judges))
