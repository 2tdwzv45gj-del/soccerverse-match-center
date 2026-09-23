from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MatchData:
    fixture_id: int
    fixture: dict[str, Any]
    events: tuple[dict[str, Any], ...]
    commentary: tuple[dict[str, Any], ...]
    substitutions: tuple[dict[str, Any], ...]


class MatchDataService:
    """Loads and normalizes all official data required by Match Center."""

    def __init__(self, mcp: Any) -> None:
        self.mcp = mcp

    def load(self, fixture_id: int) -> MatchData:
        fixture_id = int(fixture_id)

        if fixture_id <= 0:
            raise ValueError("Fixture ID must be positive")

        fixture = self.mcp.get_fixture(fixture_id)
        events = self.mcp.get_match_events(fixture_id)

        # Soccerverse can occasionally return a GOAL with a club_id
        # that conflicts with the scoring player's actual club.
        # Preserve all event data, but correct the club attribution
        # only when the player's club is one of the two fixture clubs.
        home_club_id = int(fixture["home_club"])
        away_club_id = int(fixture["away_club"])

        normalized_events = []
        player_club_cache: dict[int, int | None] = {}

        for event in events:
            normalized = dict(event)

            if str(event.get("event_type", "")).upper() == "GOAL":
                player_id = event.get("player_id")
                event_club_id = event.get("club_id")

                if player_id is not None and event_club_id is not None:
                    player_id = int(player_id)

                    if player_id not in player_club_cache:
                        try:
                            player = self.mcp.get_player_details(player_id)
                            player_club_cache[player_id] = (
                                int(player["club_id"])
                                if isinstance(player, dict)
                                and player.get("club_id") is not None
                                else None
                            )
                        except Exception:
                            player_club_cache[player_id] = None

                    player_club_id = player_club_cache[player_id]

                    if (
                        player_club_id in (home_club_id, away_club_id)
                        and int(event_club_id) != player_club_id
                    ):
                        normalized["club_id"] = player_club_id
                        normalized["club_name"] = (
                            fixture["home_club_name"]
                            if player_club_id == home_club_id
                            else fixture["away_club_name"]
                        )

            normalized_events.append(normalized)

        events = normalized_events
        commentary = self.mcp.get_match_commentary(fixture_id)
        substitutions = self.mcp.get_match_subs(fixture_id)

        if not isinstance(fixture, dict):
            raise ValueError("Invalid fixture response")

        if not isinstance(events, list):
            raise ValueError("Invalid events response")

        if isinstance(commentary, dict):
            commentary_items = commentary.get("commentary", [])
        else:
            commentary_items = commentary

        if not isinstance(commentary_items, list):
            raise ValueError("Invalid commentary response")

        if not isinstance(substitutions, list):
            raise ValueError("Invalid substitutions response")

        return MatchData(
            fixture_id=fixture_id,
            fixture=fixture,
            events=tuple(events),
            commentary=tuple(commentary_items),
            substitutions=tuple(substitutions),
        )
