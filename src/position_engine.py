from typing import Dict, List, Tuple

from src.soccerverse_position_grid import soccerverse_penalty

from src.models.team import Player


# Penalità ufficiale/ricostruita per posizione.
#
# 0%  = posizione naturale
# 1-9% = adattamento molto leggero
# 10-24% = adattamento
# 25-39% = adattamento difficile
# 40% = fuori posizione
#
# La posizione dichiarata dal giocatore in `positions`
# ha sempre priorità: penalty 0%.

POSITION_ALIASES: Dict[str, str] = {
    # Slot tattici reali restituiti da Soccerverse analyse_matchup
    # -> ruoli canonici usati dalla matrice POSITION_PENALTIES.
    "DFR": "RB",
    "DFL": "LB",
    "DFC": "CB",
    "MFR": "RM",
    "MFC": "CM",
    "MFL": "LM",
    "FWC": "FC",
}


POSITION_PENALTIES: Dict[str, Dict[str, int]] = {
    "GK": {
        "GK": 0,
    },

    "LB": {
        "LB": 0,
        "CB": 10,
        "LM": 25,
        "DML": 15,
    },

    "CB": {
        "CB": 0,
        "LB": 10,
        "RB": 10,
        "DMC": 25,
    },

    "RB": {
        "RB": 0,
        "CB": 10,
        "RM": 25,
        "DMR": 15,
    },

    "DML": {
        "DML": 0,
        "LB": 15,
        "LM": 15,
        "CM": 25,
    },

    "DMC": {
        "DMC": 0,
        "CM": 10,
        "CB": 25,
    },

    "DMR": {
        "DMR": 0,
        "RB": 15,
        "RM": 15,
        "CM": 25,
    },

    "LM": {
        "LM": 0,
        "AML": 10,
        "CM": 15,
        "LB": 30,
    },

    "CM": {
        "CM": 0,
        "DMC": 10,
        "LM": 15,
        "RM": 15,
        "AMC": 10,
    },

    "RM": {
        "RM": 0,
        "AMR": 10,
        "CM": 15,
        "RB": 30,
    },

    "AML": {
        "AML": 0,
        "LM": 10,
        "AMC": 10,
        "FL": 15,
    },

    "AMC": {
        "AMC": 0,
        "CM": 15,
        "DMC": 25,
        "AML": 10,
        "AMR": 10,
        "FC": 25,
    },

    "AMR": {
        "AMR": 0,
        "RM": 10,
        "AMC": 10,
        "FL": 25,
    },

    "FL": {
        "FL": 0,
        "AML": 15,
        "LM": 20,
        "FC": 25,
    },

    "FC": {
        "FC": 0,
        "AMC": 25,
        "FL": 25,
    },
}


def position_penalty(
    player: Player,
    requested_position: str,
) -> int:
    """Restituisce la penalità posizionale usando tutte le posizioni naturali."""

    canonical_position = POSITION_ALIASES.get(
        requested_position,
        requested_position
    )

    natural_positions = list(player.positions)

    if not natural_positions:
        natural_positions = [player.position_main]

    penalties = []

    for source_position in natural_positions:
        try:
            penalty = soccerverse_penalty(
                source_position,
                canonical_position,
            )
        except ValueError:
            continue

        penalties.append(penalty)

    if not penalties:
        return 40

    return min(penalties)


def compatibility(
    player: Player,
    requested_position: str,
) -> float:

    penalty = position_penalty(
        player,
        requested_position
    )

    return 1.0 - (penalty / 100.0)


def is_usable(
    player: Player,
    requested_position: str,
) -> bool:

    return position_penalty(
        player,
        requested_position
    ) < 40


def explain_compatibility(
    player: Player,
    requested_position: str,
) -> str:

    penalty = position_penalty(
        player,
        requested_position
    )

    if penalty == 0:
        return "naturale"

    if penalty < 10:
        return "molto adatta"

    if penalty < 25:
        return "adattamento possibile"

    if penalty < 40:
        return "adattamento difficile"

    return "fuori posizione"


def rank_players_for_position(
    players: List[Player],
    requested_position: str,
) -> List[Tuple[Player, float]]:

    ranked = []

    for player in players:

        penalty = position_penalty(
            player,
            requested_position
        )

        if penalty >= 40:
            continue

        score = compatibility(
            player,
            requested_position
        )

        ranked.append(
            (player, score)
        )

    ranked.sort(
        key=lambda item: (
            item[1],
            item[0].rating,
        ),
        reverse=True
    )

    return ranked
