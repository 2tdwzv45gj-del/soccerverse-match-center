"""Convert a GSP get_squad result into Player objects."""

from src.gsp_player_mapper import gsp_player_to_player
from src.models.team import Player


def gsp_squad_to_players(
    result: dict,
    age: int = 0,
    club_id: int | None = None,
) -> list[Player]:
    """Convert the verified GSP get_squad result into Players."""

    data = result.get("data")

    if not isinstance(data, list):
        raise ValueError(
            "GSP get_squad result does not contain "
            "a valid data list."
        )

    players: list[Player] = []

    for item in data:
        if not isinstance(item, dict):
            raise ValueError(
                "GSP squad contains a non-object player record."
            )

        if club_id is not None:
            item_club_id = int(item["club_id"])
            loaned_to_club = int(
                item.get("loaned_to_club") or 0
            )

            belongs_to_club = (
                item_club_id == int(club_id)
                or loaned_to_club == int(club_id)
            )

            if not belongs_to_club:
                raise ValueError(
                    "GSP squad contains a player from "
                    f"unexpected club {item_club_id}; "
                    f"expected {club_id}, and player is not "
                    f"loaned to that club."
                )

        players.append(
            gsp_player_to_player(
                item,
                age=age,
            )
        )

    return players
