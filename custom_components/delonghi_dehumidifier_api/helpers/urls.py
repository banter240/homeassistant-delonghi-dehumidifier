"""URL helpers."""

from __future__ import annotations

import urllib.parse


def get_query_param(url: str | None, param: str) -> str | None:
    if not url:
        return None
    query = urllib.parse.urlparse(url).query
    params = urllib.parse.parse_qs(query)
    return params.get(param, [None])[0]


def url_encode(value: str) -> str:
    return urllib.parse.quote(value)
