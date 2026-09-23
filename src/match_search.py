from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .datapack_resolver import DatapackResolver


@dataclass(frozen=True)
class MatchSearchResult:
    fixture_id: int
    home_team: str
    away_team: str
    score: str
    played: bool
    datetime: str
    competition: str


@dataclass(frozen=True)
class ClubSearchCandidate:
    club_id: int
    club_name: str
    confidence: float


@dataclass(frozen=True)
class MatchSearchResponse:
    club_id: int
    club_name: str
    matches: tuple[MatchSearchResult, ...]
    candidates: tuple[ClubSearchCandidate, ...]


class MatchSearchService:
    def __init__(self, mcp: Any, datapack: DatapackResolver | None = None) -> None:
        self.mcp = mcp
        self.datapack = datapack or DatapackResolver()

    def search(self, team_name: str) -> MatchSearchResponse:
        name = team_name.strip()

        if not name:
            raise ValueError("Team name cannot be empty")

        # Club ID is the primary technical identity.
        if name.isdigit():
            club_id = int(name)

            if club_id <= 0:
                raise ValueError(f"Invalid club ID: {name}")

            pack_club = self.datapack.get_club(club_id)
            club_name = (
                str(pack_club.get("n"))
                if pack_club and pack_club.get("n")
                else f"Club {club_id}"
            )

            resolved_candidates = (
                ClubSearchCandidate(
                    club_id=club_id,
                    club_name=club_name,
                    confidence=1.0,
                ),
            )
        else:
            candidates = self.mcp.resolve_club_name(name)

            if not candidates:
                raise ValueError(f"Club not found: {name}")

            resolved_candidates = tuple(
                ClubSearchCandidate(
                    club_id=int(candidate["id"]),
                    club_name=str(candidate["name"]),
                    confidence=float(candidate.get("confidence", 0.0)),
                )
                for candidate in candidates
            )

            club = candidates[0]
            club_id = int(club["id"])

            pack_club = self.datapack.get_club(club_id)
            club_name = (
                str(pack_club.get("n"))
                if pack_club and pack_club.get("n")
                else str(club["name"])
            )

        schedule = self.mcp.get_club_schedule(club_id)

        matches = tuple(
            sorted(
                (
                    MatchSearchResult(
                        fixture_id=int(item["fixture_id"]),
                        home_team=str(item["home_club_name"]),
                        away_team=str(item["away_club_name"]),
                        score=f'{item["home_goals"]}-{item["away_goals"]}',
                        played=bool(item["played"]),
                        datetime=str(item["datetime"]),
                        competition=str(
                            item.get("comp_name")
                            or item.get("league_name")
                            or ""
                        ),
                    )
                    for item in schedule
                ),
                key=lambda match: (match.datetime, match.fixture_id),
            )
        )

        return MatchSearchResponse(
            club_id=club_id,
            club_name=club_name,
            matches=matches,
            candidates=resolved_candidates,
        )
