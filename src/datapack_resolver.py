from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PACK_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "datapack"
    / "rincon_s4.json"
)


class DatapackResolver:
    """Read-only resolver for Soccerverse graphical/data-pack assets."""

    def __init__(self, pack_path: str | Path = DEFAULT_PACK_PATH):
        self.pack_path = Path(pack_path)
        self._load()

    def _load(self) -> None:
        with self.pack_path.open("r", encoding="utf-8") as f:
            root = json.load(f)["PackData"]

        self._player_data = root["PlayerData"]
        self._club_data = root["ClubData"]
        self._stadium_data = root["StadiumData"]
        self._league_data = root["LeagueData"]
        self._cup_data = root["CupData"]

        self._players = {str(x["id"]): x for x in self._player_data["P"]}
        self._clubs = {str(x["id"]): x for x in self._club_data["C"]}
        self._stadiums = {str(x["id"]): x for x in self._stadium_data["S"]}
        self._leagues = {str(x["id"]): x for x in self._league_data["L"]}
        self._cups = {str(x["id"]): x for x in self._cup_data["C"]}

    @staticmethod
    def _image_url(base_url: str, filename: str) -> str:
        return base_url.rstrip("/") + "/" + filename.lstrip("/")

    def get_player(self, player_id: int | str) -> dict[str, Any] | None:
        return self._players.get(str(player_id))

    def get_player_name(self, player_id: int | str) -> str | None:
        player = self.get_player(player_id)
        if not player:
            return None

        first_name = str(player.get("f", "")).strip()
        surname = str(player.get("s", "")).strip()
        full_name = " ".join(part for part in (first_name, surname) if part)

        return full_name or None

    def get_club(self, club_id: int | str) -> dict[str, Any] | None:
        return self._clubs.get(str(club_id))

    def get_club_logo(self, club_id: int | str) -> str | None:
        club = self.get_club(club_id)
        if not club:
            return None
        return self._image_url(self._club_data["baseImageUrl"], f'{club["id"]}.png')

    def get_club_colors(self, club_id: int | str) -> tuple[int, int, int] | None:
        club = self.get_club(club_id)
        if not club or not club.get("rgb"):
            return None
        try:
            values = tuple(int(x.strip()) for x in club["rgb"].split(","))
            if len(values) != 3:
                return None
            return values
        except (TypeError, ValueError):
            return None

    def get_stadium(self, stadium_id: int | str) -> dict[str, Any] | None:
        return self._stadiums.get(str(stadium_id))

    def get_stadium_image(self, stadium_id: int | str) -> str | None:
        stadium = self.get_stadium(stadium_id)
        if not stadium:
            return None
        return self._image_url(
            self._stadium_data["baseImageUrl"],
            f'{stadium["id"]}.png',
        )

    def get_league(self, league_id: int | str) -> dict[str, Any] | None:
        return self._leagues.get(str(league_id))

    def get_league_image(self, league_id: int | str) -> str | None:
        league = self.get_league(league_id)
        if not league:
            return None
        return self._image_url(
            self._league_data["baseImageUrl"],
            league["i"],
        )

    def get_cup(self, cup_id: int | str) -> dict[str, Any] | None:
        return self._cups.get(str(cup_id))

    def get_cup_image(self, cup_id: int | str) -> str | None:
        cup = self.get_cup(cup_id)
        if not cup:
            return None
        return self._image_url(
            self._cup_data["baseImageUrl"],
            cup["i"],
        )
