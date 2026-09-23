from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_DATASET = Path(
    "data/raw/mcp_historical_club_positions.json"
)


class MatchupEngine:
    """
    Historical evidence engine for Soccerverse tactical matchups.

    STATUS:
        - Historical W/D/L evidence: VERIFIED DATA
        - Tactical causality: OPEN
        - Tactical bonus/penalty formula: NOT IMPLEMENTED
        - Prediction: NOT IMPLEMENTED
    """

    def __init__(self, dataset_path: Path = DEFAULT_DATASET):
        self.dataset_path = Path(dataset_path)
        self.matchups: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        data = json.loads(
            self.dataset_path.read_text(encoding="utf-8")
        )

        for club_id, wrapper in data.items():
            raw = wrapper.get("raw_analysis", {})
            current = raw.get("current_tactics", {})
            results = raw.get("recent_results", [])

            my_formation = current.get("formation_name")
            my_formation_id = current.get("formation_id")
            my_style = current.get("play_style")

            for result in results:
                opponent_id = result.get("opponent_id")
                opponent = result.get("opponent")
                opponent_formation = result.get("formation")
                opponent_style = result.get("play_style")

                if opponent_id is None:
                    continue

                if not (
                    my_formation
                    and my_style
                    and opponent_formation
                    and opponent_style
                ):
                    continue

                self.matchups.append(
                    {
                        "club_id": int(club_id),
                        "my_formation": my_formation,
                        "my_formation_id": my_formation_id,
                        "my_style": my_style,
                        "opponent_id": opponent_id,
                        "opponent": opponent,
                        "opponent_formation": opponent_formation,
                        "opponent_style": opponent_style,
                        "date": result.get("date"),
                        "fixture_id": result.get("fixture_id"),
                        "venue": result.get("venue"),
                        "result": result.get("result"),
                        "score": result.get("score"),
                    }
                )

    @staticmethod
    def _parse_score(score: str | None) -> tuple[int, int] | None:
        if not score or "-" not in score:
            return None

        try:
            a, b = score.split("-", 1)
            return int(a), int(b)
        except (ValueError, TypeError):
            return None

    def find(
        self,
        my_formation: str,
        my_style: str,
        opponent_formation: str,
        opponent_style: str,
    ) -> dict[str, Any]:

        matches = [
            m
            for m in self.matchups
            if m["my_formation"] == my_formation
            and m["my_style"] == my_style
            and m["opponent_formation"] == opponent_formation
            and m["opponent_style"] == opponent_style
        ]

        wins = sum(m["result"] == "W" for m in matches)
        draws = sum(m["result"] == "D" for m in matches)
        losses = sum(m["result"] == "L" for m in matches)

        goals_for = 0
        goals_against = 0
        scored_matches = 0

        for match in matches:
            parsed = self._parse_score(match.get("score"))

            if parsed is None:
                continue

            gf, ga = parsed
            goals_for += gf
            goals_against += ga
            scored_matches += 1

        observations = len(matches)

        if observations == 0:
            evidence = "none"
        elif observations == 1:
            evidence = "single"
        elif observations <= 2:
            evidence = "limited"
        elif observations <= 4:
            evidence = "moderate"
        else:
            evidence = "strongest_available"

        return {
            "my_formation": my_formation,
            "my_style": my_style,
            "opponent_formation": opponent_formation,
            "opponent_style": opponent_style,
            "observations": observations,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "scored_matches": scored_matches,
            "evidence": evidence,
            "matches": matches,
        }

    def formation_matrix(self) -> list[dict[str, Any]]:
        groups = defaultdict(list)

        for match in self.matchups:
            key = (
                match["my_formation"],
                match["opponent_formation"],
            )
            groups[key].append(match)

        output = []

        for (
            my_formation,
            opponent_formation,
        ), matches in groups.items():

            results = [
                m["result"]
                for m in matches
                if m["result"] in ("W", "D", "L")
            ]

            output.append(
                {
                    "my_formation": my_formation,
                    "opponent_formation": opponent_formation,
                    "observations": len(matches),
                    "wins": results.count("W"),
                    "draws": results.count("D"),
                    "losses": results.count("L"),
                }
            )

        return sorted(
            output,
            key=lambda x: (
                -x["observations"],
                x["my_formation"],
                x["opponent_formation"],
            ),
        )
