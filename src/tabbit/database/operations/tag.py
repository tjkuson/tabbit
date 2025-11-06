from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.judge import Judge
from tabbit.database.schemas.speaker import Speaker
from tabbit.database.schemas.tag import ListTagsQuery
from tabbit.database.schemas.tag import Tag
from tabbit.database.schemas.tag import TagCreate
from tabbit.database.schemas.tag import TagPatch
from tabbit.sentinel import Unset


async def create_tag(
    session: AsyncSession,
    tag_create: TagCreate,
) -> int:
    """Create a tag in the database.

    Args:
        session: The database session to use for the operation.
        tag_create: The tag creation data.

    Returns:
        The ID of the created tag.
    """
    tag_model = models.Tag(
        name=tag_create.name,
        tournament_id=tag_create.tournament_id,
    )
    session.add(tag_model)
    await session.commit()
    return tag_model.id


async def get_tag(
    session: AsyncSession,
    tag_id: int,
) -> Tag | None:
    """Get a tag via its ID.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag to retrieve.

    Returns:
        The tag if found, None otherwise.
    """
    tag_model = await session.get(models.Tag, tag_id)
    if tag_model is None:
        return None
    else:
        return Tag(
            id=tag_model.id,
            tournament_id=tag_model.tournament_id,
            name=tag_model.name,
        )


async def delete_tag(
    session: AsyncSession,
    tag_id: int,
) -> int | None:
    """Delete a tag via its ID.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag to delete.

    Returns:
        The tag ID if deleted, None if the tag was not found.
    """
    tag_model = await session.get(models.Tag, tag_id)
    if tag_model is None:
        return None

    await session.delete(tag_model)
    await session.commit()
    return tag_id


async def patch_tag(
    session: AsyncSession,
    tag_id: int,
    tag_patch: TagPatch,
) -> Tag | None:
    """Patch a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag to patch.
        tag_patch: The partial tag data to apply.

    Returns:
        The updated tag, None if no tag was found with the given ID.
    """
    tag_model = await session.get(models.Tag, tag_id)
    if tag_model is None:
        return None

    if tag_patch.name is not Unset:
        tag_model.name = tag_patch.name

    await session.commit()
    return Tag(
        id=tag_model.id,
        tournament_id=tag_model.tournament_id,
        name=tag_model.name,
    )


async def list_tags(
    session: AsyncSession,
    list_tags_query: ListTagsQuery,
) -> list[Tag]:
    """List tags with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_tags_query: The query parameters.

    Returns:
        The list of tags matching the criteria.
    """
    query = (
        select(models.Tag).offset(list_tags_query.offset).limit(list_tags_query.limit)
    )
    if list_tags_query.name is not None:
        query = query.filter(models.Tag.name.ilike(f"%{list_tags_query.name}%"))
    if list_tags_query.tournament_id is not None:
        query = query.filter(models.Tag.tournament_id == list_tags_query.tournament_id)
    if list_tags_query.speaker_id is not None:
        query = query.join(models.SpeakerTag).filter(
            models.SpeakerTag.speaker_id == list_tags_query.speaker_id
        )
    if list_tags_query.judge_id is not None:
        query = query.join(models.JudgeTag).filter(
            models.JudgeTag.judge_id == list_tags_query.judge_id
        )

    result = await session.execute(query)
    tags = result.scalars().all()
    return [
        Tag(
            id=tag.id,
            tournament_id=tag.tournament_id,
            name=tag.name,
        )
        for tag in tags
    ]


async def add_speakers_to_tag(
    session: AsyncSession,
    tag_id: int,
    speaker_ids: list[int],
) -> int | None:
    """Add speakers to a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.
        speaker_ids: The IDs of the speakers to add.

    Returns:
        The tag ID if successful, None if the tag was not found.
    """
    tag_model = await session.get(models.Tag, tag_id)
    if tag_model is None:
        return None

    speaker_tags = [
        models.SpeakerTag(speaker_id=speaker_id, tag_id=tag_id)
        for speaker_id in speaker_ids
    ]
    session.add_all(speaker_tags)
    await session.commit()
    return tag_id


async def remove_speaker_from_tag(
    session: AsyncSession,
    tag_id: int,
    speaker_id: int,
) -> int | None:
    """Remove a speaker from a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.
        speaker_id: The ID of the speaker to remove.

    Returns:
        The tag ID if successful, None if the association was not found.
    """
    stmt = delete(models.SpeakerTag).where(
        models.SpeakerTag.tag_id == tag_id, models.SpeakerTag.speaker_id == speaker_id
    )
    result = await session.execute(stmt)
    await session.commit()

    # https://github.com/sqlalchemy/sqlalchemy/issues/12913
    if result.rowcount == 0:  # type: ignore[attr-defined]
        return None
    return tag_id


async def list_speakers_for_tag(
    session: AsyncSession,
    tag_id: int,
) -> list[Speaker]:
    """List speakers associated with a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.

    Returns:
        The list of speakers associated with the tag.
    """
    query = (
        select(models.Speaker)
        .join(models.SpeakerTag)
        .filter(models.SpeakerTag.tag_id == tag_id)
    )
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


async def add_judges_to_tag(
    session: AsyncSession,
    tag_id: int,
    judge_ids: list[int],
) -> int | None:
    """Add judges to a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.
        judge_ids: The IDs of the judges to add.

    Returns:
        The tag ID if successful, None if the tag was not found.
    """
    tag_model = await session.get(models.Tag, tag_id)
    if tag_model is None:
        return None

    for judge_id in judge_ids:
        judge_tag = models.JudgeTag(judge_id=judge_id, tag_id=tag_id)
        session.add(judge_tag)

    await session.commit()
    return tag_id


async def remove_judge_from_tag(
    session: AsyncSession,
    tag_id: int,
    judge_id: int,
) -> int | None:
    """Remove a judge from a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.
        judge_id: The ID of the judge to remove.

    Returns:
        The tag ID if successful, None if the association was not found.
    """
    stmt = delete(models.JudgeTag).where(
        models.JudgeTag.tag_id == tag_id, models.JudgeTag.judge_id == judge_id
    )
    result = await session.execute(stmt)
    await session.commit()

    # https://github.com/sqlalchemy/sqlalchemy/issues/12913
    if result.rowcount == 0:  # type: ignore[attr-defined]
        return None
    return tag_id


async def list_judges_for_tag(
    session: AsyncSession,
    tag_id: int,
) -> list[Judge]:
    """List judges associated with a tag.

    Args:
        session: The database session to use for the operation.
        tag_id: The ID of the tag.

    Returns:
        The list of judges associated with the tag.
    """
    query = (
        select(models.Judge)
        .join(models.JudgeTag)
        .filter(models.JudgeTag.tag_id == tag_id)
    )
    result = await session.execute(query)
    judges = result.scalars().all()
    return [
        Judge(
            id=judge.id,
            tournament_id=judge.tournament_id,
            name=judge.name,
        )
        for judge in judges
    ]
