"""Root views router for HTML interface."""

import http
from typing import Annotated
from typing import Final

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from tabbit.database.operations import tournament as crud
from tabbit.database.schemas.tournament import ListTournamentsQuery
from tabbit.database.session import session_manager
from tabbit.http.views.templating import templates

views_router: Final = APIRouter(prefix="")


@views_router.get("/")
async def tournaments_view(
    request: Request,
    session: Annotated[AsyncSession, Depends(session_manager.session)],
) -> Response:
    """Render the tournaments page.

    Returns an HTML page displaying all tournaments in a table.
    """
    query = ListTournamentsQuery()
    tournaments = await crud.list_tournaments(session, query)
    return templates.TemplateResponse(
        request=request,
        name="tournaments.html",
        context={"tournaments": tournaments},
        status_code=http.HTTPStatus.OK,
    )
