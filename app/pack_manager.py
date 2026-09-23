import json
from pathlib import Path


DEFAULT_PACK_PATH = Path("/tmp/rincon_s4.json")


class PackManager:
    """Layer anagrafico del Community Pack S4.

    NON contiene logica tattica.
    NON modifica i dati GSP.
    Serve esclusivamente per risolvere nomi di club e giocatori.
    """

    def __init__(self, pack_path: Path = DEFAULT_PACK_PATH):
        self.pack_path = Path(pack_path)

        self.club_names: dict[int, str] = {}
        self.player_names: dict[int, str] = {}

        self.loaded = False

    def load(self) -> None:
        if not self.pack_path.exists():
            raise FileNotFoundError(
                f"Community Pack non trovato: {self.pack_path}"
            )

        with self.pack_path.open("r", encoding="utf-8") as f:
            pack = json.load(f)["PackData"]

        for club in pack["ClubData"]["C"]:
            self.club_names[int(club["id"])] = club["n"]

        for player in pack["PlayerData"]["P"]:
            first = player.get("f", "").strip()
            last = player.get("s", "").strip()
            name = f"{first} {last}".strip()

            if name:
                self.player_names[int(player["id"])] = name

        self.loaded = True

    def get_club_name(self, club_id: int) -> str | None:
        if not self.loaded:
            self.load()

        return self.club_names.get(int(club_id))

    def get_player_name(self, player_id: int) -> str | None:
        if not self.loaded:
            self.load()

        return self.player_names.get(int(player_id))

    def stats(self) -> dict:
        return {
            "clubs": len(self.club_names),
            "players": len(self.player_names),
        }
