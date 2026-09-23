from typing import Dict

from src.models.team import Player


ROLE_WEIGHTS: Dict[str, Dict[str, float]] = {

    "GK": {
        "rating_gk": 0.70,
        "rating": 0.20,
        "fitness": 0.10,
    },

    "LB": {
        "rating": 0.35,
        "rating_tackling": 0.30,
        "rating_passing": 0.15,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "CB": {
        "rating": 0.35,
        "rating_tackling": 0.40,
        "rating_passing": 0.10,
        "rating_stamina": 0.05,
        "fitness": 0.10,
    },

    "RB": {
        "rating": 0.35,
        "rating_tackling": 0.30,
        "rating_passing": 0.15,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "DML": {
        "rating": 0.30,
        "rating_tackling": 0.30,
        "rating_passing": 0.20,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "DMC": {
        "rating": 0.25,
        "rating_tackling": 0.30,
        "rating_passing": 0.25,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "DMR": {
        "rating": 0.30,
        "rating_tackling": 0.30,
        "rating_passing": 0.20,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "LM": {
        "rating": 0.30,
        "rating_passing": 0.25,
        "rating_shooting": 0.15,
        "rating_stamina": 0.20,
        "fitness": 0.10,
    },

    "CM": {
        "rating": 0.25,
        "rating_passing": 0.35,
        "rating_tackling": 0.15,
        "rating_stamina": 0.15,
        "fitness": 0.10,
    },

    "RM": {
        "rating": 0.30,
        "rating_passing": 0.25,
        "rating_shooting": 0.15,
        "rating_stamina": 0.20,
        "fitness": 0.10,
    },

    "AML": {
        "rating": 0.25,
        "rating_passing": 0.20,
        "rating_shooting": 0.30,
        "rating_stamina": 0.15,
        "fitness": 0.10,
    },

    "AMC": {
        "rating": 0.20,
        "rating_passing": 0.35,
        "rating_shooting": 0.25,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },

    "AMR": {
        "rating": 0.25,
        "rating_passing": 0.20,
        "rating_shooting": 0.30,
        "rating_stamina": 0.15,
        "fitness": 0.10,
    },

    "FL": {
        "rating": 0.25,
        "rating_passing": 0.20,
        "rating_shooting": 0.30,
        "rating_stamina": 0.15,
        "fitness": 0.10,
    },

    "FC": {
        "rating": 0.25,
        "rating_shooting": 0.45,
        "rating_passing": 0.10,
        "rating_stamina": 0.10,
        "fitness": 0.10,
    },
}


def get_attribute_value(
    player: Player,
    attribute: str,
) -> float:

    return float(
        getattr(
            player,
            attribute,
            0
        )
    )


def evaluate_player(
    player: Player,
    position: str,
) -> float:

    weights = ROLE_WEIGHTS.get(
        position
    )

    if not weights:
        return 0.0

    total = 0.0

    for attribute, weight in weights.items():

        value = get_attribute_value(
            player,
            attribute
        )

        total += value * weight

    return total


def player_profile(
    player: Player,
    position: str,
) -> Dict:

    weights = ROLE_WEIGHTS.get(
        position,
        {}
    )

    attributes = {}

    for attribute in weights:

        attributes[attribute] = get_attribute_value(
            player,
            attribute
        )

    score = evaluate_player(
        player,
        position
    )

    return {
        "player_id": player.player_id,
        "position": position,
        "score": score,
        "attributes": attributes,
    }