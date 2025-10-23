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

from tabbit.database.operations import speaker as crud
from tabbit.database.schemas.speaker import ListSpeakersQuery as DBListSpeakersQuery
from tabbit.database.schemas.speaker import SpeakerCreate as DBSpeakerCreate
from tabbit.database.session import session_manager
from tabbit.http.api.enums import Tags
from tabbit.http.api.schemas.speaker import ListSpeakersQuery
from tabbit.http.api.schemas.speaker import Speaker
from tabbit.http.api.schemas.speaker import SpeakerCreate
from tabbit.http.api.schemas.speaker import SpeakerID
from tabbit.http.api.schemas.speaker import SpeakerPatch
from tabbit.http.api.util import not_found_response

logger = logging.getLogger(__name__)

speakers_router: Final = APIRouter(
    prefix="/speaker",
    tags=[Tags.SPEAKER],
)


@speakers_router.post(
    "/create",
    response_model=SpeakerID,
)
async def create_speaker(
    speaker: SpeakerCreate,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Create a speaker.

    Returns the speaker ID upon creation.
    """
    db_speaker = DBSpeakerCreate(**speaker.model_dump())
    speaker_id = SpeakerID(id=await crud.create_speaker(session, db_speaker))
    logger.info("Created speaker.", extra={"speaker_id": speaker_id})
    return JSONResponse(content=jsonable_encoder(speaker_id))


@speakers_router.get(
    "/{speaker_id}",
    response_model=Speaker,
    responses=not_found_response("speaker"),
)
async def get_speaker(
    speaker_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Get a speaker using its ID.

    Returns the speaker if found; otherwise, 404 Not Found.
    """
    db_speaker = await crud.get_speaker(session, speaker_id)

    if db_speaker is None:
        logger.info("Speaker not found.", extra={"speaker_id": speaker_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Speaker not found."},
        )
    else:
        speaker = Speaker.model_validate(db_speaker)
        logger.info("Got speaker by ID.", extra={"speaker_id": speaker_id})
        return JSONResponse(content=jsonable_encoder(speaker))


@speakers_router.delete(
    "/{speaker_id}",
    status_code=http.HTTPStatus.NO_CONTENT,
    responses=not_found_response("speaker"),
)
async def delete_speaker(
    speaker_id: int,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Delete an existing speaker.

    Returns the speaker if found; otherwise, 404 Not Found.
    """
    speaker = await crud.delete_speaker(session, speaker_id)

    if speaker is None:
        logger.info("Speaker not found.", extra={"speaker_id": speaker_id})
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Speaker not found."},
        )
    else:
        logger.info("Deleted speaker by ID.", extra={"speaker_id": speaker_id})
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


@speakers_router.patch(
    "/{speaker_id}",
    response_model=Speaker,
    responses=not_found_response("speaker"),
)
async def patch_speaker(
    speaker_id: int,
    speaker_patch: SpeakerPatch,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """Patch an existing speaker.

    Returns the updated speaker.
    """
    db_speaker = await crud.patch_speaker(session, speaker_id, name=speaker_patch.name)

    if db_speaker is None:
        logger.info(
            "Speaker not found.",
            extra={"speaker_patch": speaker_patch},
        )
        return JSONResponse(
            status_code=http.HTTPStatus.NOT_FOUND,
            content={"message": "Speaker not found."},
        )
    else:
        speaker = Speaker.model_validate(db_speaker)
        logger.info(
            "Patched speaker.",
            extra={"speaker_patch": speaker_patch},
        )
        return JSONResponse(content=jsonable_encoder(speaker))


@speakers_router.get(
    "/",
    response_model=list[Speaker],
)
async def list_speakers(
    query: Annotated[ListSpeakersQuery, Query()],
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> JSONResponse:
    """List speakers with optional filtering and pagination.

    Returns an empty list if none are found.
    """
    db_query = DBListSpeakersQuery(**query.model_dump())
    db_speakers = await crud.list_speakers(session, db_query)
    speakers = [Speaker.model_validate(db_speaker) for db_speaker in db_speakers]
    logger.info("Listed speakers.", extra={"query": query})
    return JSONResponse(content=jsonable_encoder(speakers))
