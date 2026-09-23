from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MatchEvent:
    match_event_id: int
    event_type: str
    player_id: Optional[int]
    club_id: Optional[int]
    time: int
    goal_type: Optional[str]
    season_id: Optional[int]
    player_name: Optional[str]
    club_name: Optional[str]
    time_minutes: Optional[str]
    time_display: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> "MatchEvent":
        return cls(
            match_event_id=int(data["match_event_id"]),
            event_type=data["event_type"],
            player_id=(
                int(data["player_id"])
                if data.get("player_id") is not None else None
            ),
            club_id=(
                int(data["club_id"])
                if data.get("club_id") is not None else None
            ),
            time=int(data["time"]),
            goal_type=data.get("goal_type"),
            season_id=(
                int(data["season_id"])
                if data.get("season_id") is not None else None
            ),
            player_name=data.get("player_name"),
            club_name=data.get("club_name"),
            time_minutes=data.get("time_minutes"),
            time_display=data.get("time_display"),
        )


@dataclass(frozen=True)
class CommentarySubEvent:
    comm_sub_event_id: int
    comm_event_id: int
    category: str
    time: int
    player_one_id: Optional[int]
    player_two_id: Optional[int]
    club_one_id: Optional[int]
    player_one_name: Optional[str]
    player_two_name: Optional[str]
    club_one_name: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> "CommentarySubEvent":
        return cls(
            comm_sub_event_id=int(data["comm_sub_event_id"]),
            comm_event_id=int(data["comm_event_id"]),
            category=data["category"],
            time=int(data["time"]),
            player_one_id=(
                int(data["player_one_id"])
                if data.get("player_one_id") is not None else None
            ),
            player_two_id=(
                int(data["player_two_id"])
                if data.get("player_two_id") is not None else None
            ),
            club_one_id=(
                int(data["club_one_id"])
                if data.get("club_one_id") is not None else None
            ),
            player_one_name=data.get("player_one_name"),
            player_two_name=data.get("player_two_name"),
            club_one_name=data.get("club_one_name"),
        )
