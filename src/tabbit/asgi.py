from __future__ import annotations

from fastapi import FastAPI

from tabbit.http.root import root_router


def setup_app() -> FastAPI:
    """Configure and initialize the ASGI application.

    Returns:
        An ASGI application.
    """
    app = FastAPI(title="Tabbit")
    app.include_router(root_router)
    return app


app = setup_app()
