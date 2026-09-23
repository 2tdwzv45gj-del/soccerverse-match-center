"""Convert verified Soccerverse GSP player records into Player objects."""

from src.models.team import Player
from src.gsp_position_mapper import (
    decode_main_position,
    decode_position_mask,
)


def gsp_player_to_player(data: dict, age: int = 0) -> Player:
    """Convert one GSP player record into the project's Player model.

    `age` is intentionally supplied by the caller because the verified
    GSP response exposes `dob`, not an already-computed age.
    """

    main_position = decode_main_position(
        int(data["position"])
    )

    positions = decode_position_mask(
        int(data["multi_position"])
    )

    if not positions:
        positions = [main_position]

    if main_position not in positions:
        positions = [main_position, *positions]

    return Player(
        player_id=int(data["player_id"]),
        position_main=main_position,
        positions=positions,
        rating=int(data["rating"]),
        rating_gk=int(data["rating_gk"]),
        rating_tackling=int(data["rating_tackling"]),
        rating_passing=int(data["rating_passing"]),
        rating_shooting=int(data["rating_shooting"]),
        rating_stamina=int(data["rating_stamina"]),
        rating_aggression=int(data["rating_aggression"]),
        fitness=int(data["fitness"]),
        morale=int(data["morale"]),
        concerns=int(data["concerns"]),
        form=str(data["form"]),
        injured=int(data["injured"]),
        banned=int(data["banned"]),
        age=int(age),
    )
