from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.motion import ListMotionsQuery
from tabbit.database.schemas.motion import Motion
from tabbit.database.schemas.motion import MotionCreate
from tabbit.database.schemas.motion import MotionPatch
from tabbit.sentinel import Unset


async def create_motion(
    session: AsyncSession,
    motion_create: MotionCreate,
) -> int:
    """Create a motion in the database.

    Args:
        session: The database session to use for the operation.
        motion_create: The motion creation data.

    Returns:
        The ID of the created motion.
    """
    motion = models.Motion(
        round_id=motion_create.round_id,
        text=motion_create.text,
        infoslide=motion_create.infoslide,
    )
    session.add(motion)
    await session.commit()
    return motion.id


async def get_motion(
    session: AsyncSession,
    motion_id: int,
) -> Motion | None:
    """Get a motion via its ID.

    Args:
        session: The database session to use for the operation.
        motion_id: The ID of the motion to retrieve.

    Returns:
        The motion if found, None otherwise.
    """
    motion = await session.get(models.Motion, motion_id)
    if motion is None:
        return None
    else:
        return Motion(
            id=motion.id,
            round_id=motion.round_id,
            text=motion.text,
            infoslide=motion.infoslide,
        )


async def delete_motion(
    session: AsyncSession,
    motion_id: int,
) -> int | None:
    """Delete a motion via its ID.

    Args:
        session: The database session to use for the operation.
        motion_id: The ID of the motion to delete.

    Returns:
        The motion ID if deleted, None if the motion was not found.
    """
    motion = await session.get(models.Motion, motion_id)
    if motion is None:
        return None

    await session.delete(motion)
    await session.commit()
    return motion_id


async def patch_motion(
    session: AsyncSession,
    motion_id: int,
    motion_patch: MotionPatch,
) -> Motion | None:
    """Patch a motion.

    Args:
        session: The database session to use for the operation.
        motion_id: The ID of the motion to patch.
        motion_patch: The partial motion data to apply.

    Returns:
        The updated motion, None if no motion was found with the given ID.
    """
    motion = await session.get(models.Motion, motion_id)
    if motion is None:
        return None

    if motion_patch.text is not Unset:
        motion.text = motion_patch.text
    if motion_patch.infoslide is not Unset:
        motion.infoslide = motion_patch.infoslide

    await session.commit()
    return Motion(
        id=motion.id,
        round_id=motion.round_id,
        text=motion.text,
        infoslide=motion.infoslide,
    )


async def list_motions(
    session: AsyncSession,
    list_motions_query: ListMotionsQuery,
) -> list[Motion]:
    """List motions with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_motions_query: The query parameters.

    Returns:
        The list of motions matching the criteria.
    """
    query = (
        select(models.Motion)
        .offset(list_motions_query.offset)
        .limit(list_motions_query.limit)
    )
    if list_motions_query.text is not None:
        query = query.filter(models.Motion.text.ilike(f"%{list_motions_query.text}%"))
    if list_motions_query.round_id is not None:
        query = query.filter(models.Motion.round_id == list_motions_query.round_id)

    result = await session.execute(query)
    motions = result.scalars().all()
    return [
        Motion(
            id=motion.id,
            round_id=motion.round_id,
            text=motion.text,
            infoslide=motion.infoslide,
        )
        for motion in motions
    ]
