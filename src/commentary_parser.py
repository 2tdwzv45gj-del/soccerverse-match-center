from __future__ import annotations

from typing import Any

from .commentary_events import CommentarySubEvent


def parse_match_commentary_response(
    response: dict[str, Any],
) -> tuple[CommentarySubEvent, ...]:
    """
    Convert the official MCP get_match_commentary response into
    normalized CommentarySubEvent objects.

    The MCP envelope itself is discarded after validation.
    The original event fields are preserved by CommentarySubEvent.
    """
    if not isinstance(response, dict):
        raise TypeError("Commentary response must be a dictionary")

    rows = response.get("commentary")

    if rows is None:
        raise ValueError("Commentary response has no 'commentary' field")

    if not isinstance(rows, list):
        raise TypeError("'commentary' must be a list")

    return tuple(
        CommentarySubEvent.from_dict(row)
        for row in rows
    )
