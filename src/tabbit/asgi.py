from fastapi import FastAPI

from tabbit.http.api.root import api_router
from tabbit.http.root import root_router


def setup_app() -> FastAPI:
    """Configure and initialize the ASGI application.

    Returns:
        An ASGI application.
    """
    app = FastAPI(title="Tabbit")
    app.include_router(root_router)
    app.include_router(api_router)
    return app


app = setup_app()
