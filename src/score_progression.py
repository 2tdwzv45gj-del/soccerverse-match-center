from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScoreSnapshot:
    match_minute: int
    home_score: int
    away_score: int


class ScoreProgressionEngine:
    """Builds the official score progression from match events."""

    def __init__(self, fixture: dict[str, Any], events: tuple[dict[str, Any], ...] | list[dict[str, Any]]) -> None:
        self.fixture = fixture
        self.events = tuple(events)

        self.home_club_id = int(fixture["home_club"])
        self.away_club_id = int(fixture["away_club"])

    def snapshots(self) -> tuple[ScoreSnapshot, ...]:
        home_score = 0
        away_score = 0
        result: list[ScoreSnapshot] = []

        # Soccerverse can emit a GOAL immediately followed by
        # GOALCANCELLED for the same player, club and minute.
        # The cancelled goal must not alter the official score.
        cancelled_goals = {
            (
                int(event.get("time", 0)),
                int(event.get("club_id")),
                int(event.get("player_id", event.get("event_player_id"))),
            )
            for event in self.events
            if str(event.get("event_type", "")).upper() == "GOALCANCELLED"
            and event.get("club_id") is not None
            and event.get("player_id", event.get("event_player_id")) is not None
        }

        goal_events = sorted(
            (
                event
                for event in self.events
                if str(event.get("event_type", "")).upper() == "GOAL"
                and (
                    int(event.get("time", 0)),
                    int(event.get("club_id")),
                    int(event.get("player_id", event.get("event_player_id"))),
                )
                not in cancelled_goals
            ),
            key=lambda event: (
                int(event.get("time", 0)),
                int(event.get("match_event_id", 0)),
            ),
        )

        for event in goal_events:
            club_id = int(event["club_id"])

            if club_id == self.home_club_id:
                home_score += 1
            elif club_id == self.away_club_id:
                away_score += 1
            else:
                raise ValueError(
                    f"Goal belongs to unknown club {club_id}"
                )

            result.append(
                ScoreSnapshot(
                    match_minute=int(event["time"]),
                    home_score=home_score,
                    away_score=away_score,
                )
            )

        return tuple(result)

    def score_at(self, match_minute: int) -> ScoreSnapshot:
        if match_minute < 0:
            raise ValueError("Match minute cannot be negative")

        home_score = 0
        away_score = 0

        for snapshot in self.snapshots():
            if snapshot.match_minute > match_minute:
                break

            home_score = snapshot.home_score
            away_score = snapshot.away_score

        return ScoreSnapshot(
            match_minute=match_minute,
            home_score=home_score,
            away_score=away_score,
        )
