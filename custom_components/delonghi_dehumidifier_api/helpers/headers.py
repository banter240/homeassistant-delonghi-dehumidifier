"""HTTP headers."""

from __future__ import annotations

from ..const import (
    API_USER_AGENT,
    AUTH_TOKEN_PREFIX,
    AUTHORIZATION_HEADER,
    BROWSER_USER_AGENT,
    CONTENT_TYPE_FORM,
    CONTENT_TYPE_JSON,
    TOKEN_USER_AGENT,
)


def browser_headers() -> dict[str, str]:
    return {"User-Agent": BROWSER_USER_AGENT}


def token_json_headers() -> dict[str, str]:
    return {
        "User-Agent": TOKEN_USER_AGENT,
        "Content-Type": CONTENT_TYPE_JSON,
    }


def token_form_headers() -> dict[str, str]:
    return {
        "User-Agent": TOKEN_USER_AGENT,
        "Authorization": AUTHORIZATION_HEADER,
        "Content-Type": CONTENT_TYPE_FORM,
    }


def token_user_agent_headers() -> dict[str, str]:
    return {"User-Agent": TOKEN_USER_AGENT}


def api_headers(access_token: str, *, json_body: bool = False) -> dict[str, str]:
    headers = {
        "User-Agent": API_USER_AGENT,
        "Authorization": f"{AUTH_TOKEN_PREFIX}{access_token}",
    }
    if json_body:
        headers["Content-Type"] = CONTENT_TYPE_JSON
    return headers
