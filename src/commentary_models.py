from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fixture:
    fixture_id: int
    home_club_id: int
    away_club_id: int
    home_club_name: str
    away_club_name: str
    stadium_id: Optional[int]
    comp_type: int
    comp_type_name: str
    country_id: Optional[str]
    league_name: Optional[str]
    comp_name: Optional[str]
    turn_id: Optional[int]
    datetime: Optional[str]
    datetime_utc: Optional[str]
    date_formatted: Optional[str]
    day_of_week: Optional[str]
    played: bool
    home_goals: Optional[int]
    away_goals: Optional[int]
    home_pen_score: Optional[int]
    away_pen_score: Optional[int]
    penalties: bool
    attendance: Optional[int]

    @classmethod
    def from_dict(cls, data: dict) -> "Fixture":
        return cls(
            fixture_id=int(data["fixture_id"]),
            home_club_id=int(data["home_club"]),
            away_club_id=int(data["away_club"]),
            home_club_name=data["home_club_name"],
            away_club_name=data["away_club_name"],
            stadium_id=(
                int(data["stadium_id"])
                if data.get("stadium_id") is not None
                else None
            ),
            comp_type=int(data.get("comp_type", 0)),
            comp_type_name=data.get("comp_type_name", ""),
            country_id=data.get("country_id"),
            league_name=data.get("league_name"),
            comp_name=data.get("comp_name"),
            turn_id=(
                int(data["turn_id"])
                if data.get("turn_id") is not None
                else None
            ),
            datetime=data.get("datetime"),
            datetime_utc=data.get("datetime_utc"),
            date_formatted=data.get("date_formatted"),
            day_of_week=data.get("day_of_week"),
            played=bool(data.get("played", 0)),
            home_goals=(
                int(data["home_goals"])
                if data.get("home_goals") is not None
                else None
            ),
            away_goals=(
                int(data["away_goals"])
                if data.get("away_goals") is not None
                else None
            ),
            home_pen_score=(
                int(data["home_pen_score"])
                if data.get("home_pen_score") is not None
                else None
            ),
            away_pen_score=(
                int(data["away_pen_score"])
                if data.get("away_pen_score") is not None
                else None
            ),
            penalties=bool(data.get("penalties", 0)),
            attendance=(
                int(data["attendance"])
                if data.get("attendance") is not None
                else None
            ),
        )
