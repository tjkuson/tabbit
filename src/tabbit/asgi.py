import http
from pathlib import Path
from typing import Final

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from tabbit.http.api.root import api_router
from tabbit.http.root import root_router
from tabbit.http.views.root import views_router

_VIEWS_DIR: Final = Path(__file__).parent / "http" / "views"
_TEMPLATES_DIR: Final = _VIEWS_DIR / "templates"
_STATIC_DIR: Final = _VIEWS_DIR / "static"

_templates: Final = Jinja2Templates(directory=_TEMPLATES_DIR)


def setup_app() -> FastAPI:
    """Configure and initialize the ASGI application.

    Returns:
        An ASGI application.
    """
    app = FastAPI(title="Tabbit")

    @app.exception_handler(StarletteHTTPException)
    async def custom_404_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> Response:
        """Handle 404 errors.

        Return HTML for non-API routes, JSON for API routes.
        """
        if exc.status_code != http.HTTPStatus.NOT_FOUND:  # pragma: no cover
            raise exc

        if request.url.path.startswith("/v1/"):
            return JSONResponse(
                status_code=http.HTTPStatus.NOT_FOUND,
                content={"detail": exc.detail},
            )
        else:
            return _templates.TemplateResponse(
                request=request,
                name="404.html",
                status_code=http.HTTPStatus.NOT_FOUND,
            )

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    app.include_router(root_router)
    app.include_router(api_router)
    app.include_router(views_router)

    return app


app: Final = setup_app()
