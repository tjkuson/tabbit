from __future__ import annotations

# https://fastapi.tiangolo.com/advanced/additional-responses/
type APIRouterResponses = dict[str | int, dict[str, object]]


def not_found_response(name: str) -> APIRouterResponses:
    title = name.title()
    return {
        404: {"description": f"{title} not found."},
    }
