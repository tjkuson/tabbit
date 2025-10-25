from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.speaker import ListSpeakersQuery
from tabbit.database.schemas.speaker import Speaker
from tabbit.database.schemas.speaker import SpeakerCreate


async def create_speaker(
    session: AsyncSession,
    speaker_create: SpeakerCreate,
) -> int:
    """Create a speaker in the database.

    Args:
        session: The database session to use for the operation.
        speaker_create: The speaker creation data.

    Returns:
        The ID of the created speaker.
    """
    speaker_model = models.Speaker(
        name=speaker_create.name,
        team_id=speaker_create.team_id,
    )
    session.add(speaker_model)
    await session.commit()
    return speaker_model.id


async def get_speaker(
    session: AsyncSession,
    speaker_id: int,
) -> Speaker | None:
    """Get a speaker via its ID.

    Args:
        session: The database session to use for the operation.
        speaker_id: The ID of the speaker to retrieve.

    Returns:
        The speaker if found, None otherwise.
    """
    speaker_model = await session.get(models.Speaker, speaker_id)
    if speaker_model is None:
        return None
    else:
        return Speaker(
            id=speaker_model.id,
            team_id=speaker_model.team_id,
            name=speaker_model.name,
        )


async def delete_speaker(
    session: AsyncSession,
    speaker_id: int,
) -> int | None:
    """Delete a speaker via its ID.

    Args:
        session: The database session to use for the operation.
        speaker_id: The ID of the speaker to delete.

    Returns:
        The speaker ID if deleted, None if the speaker was not found.
    """
    speaker_model = await session.get(models.Speaker, speaker_id)
    if speaker_model is None:
        return None

    await session.delete(speaker_model)
    await session.commit()
    return speaker_id


async def patch_speaker(
    session: AsyncSession,
    speaker_id: int,
    name: str | None = None,
) -> Speaker | None:
    """Patch a speaker.

    Args:
        session: The database session to use for the operation.
        speaker_id: The ID of the speaker to patch.
        name: The new name for the speaker, if provided.

    Returns:
        The updated speaker, None if no speaker was found with the given ID.
    """
    speaker_model = await session.get(models.Speaker, speaker_id)
    if speaker_model is None:
        return None

    if name is not None:
        speaker_model.name = name
    await session.commit()
    return Speaker(
        id=speaker_model.id,
        team_id=speaker_model.team_id,
        name=speaker_model.name,
    )


async def list_speakers(
    session: AsyncSession,
    list_speakers_query: ListSpeakersQuery,
) -> list[Speaker]:
    """List speakers with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_speakers_query: The query parameters.

    Returns:
        The list of speakers matching the criteria.
    """
    query = (
        select(models.Speaker)
        .offset(list_speakers_query.offset)
        .limit(list_speakers_query.limit)
    )
    if list_speakers_query.name is not None:
        query = query.filter(models.Speaker.name.ilike(f"%{list_speakers_query.name}%"))
    if list_speakers_query.team_id is not None:
        query = query.filter(models.Speaker.team_id == list_speakers_query.team_id)

    result = await session.execute(query)
    speakers = result.scalars().all()
    return [
        Speaker(
            id=speaker.id,
            team_id=speaker.team_id,
            name=speaker.name,
        )
        for speaker in speakers
    ]
