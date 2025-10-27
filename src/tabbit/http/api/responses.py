import http

# https://fastapi.tiangolo.com/advanced/additional-responses/
type APIRouterResponses = dict[str | int, dict[str, object]]


def not_found_response(name: str) -> APIRouterResponses:
    title = name.title()
    return {
        http.HTTPStatus.NOT_FOUND: {"description": f"{title} not found."},
    }


def conflict_response(message: str) -> APIRouterResponses:
    return {
        http.HTTPStatus.CONFLICT: {"description": message},
    }
