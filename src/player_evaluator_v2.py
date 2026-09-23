from typing import Dict

from src.models.team import Player
from src.effective_skills import effective_skills
from src.player_state import get_player_state


ROLE_WEIGHTS_V2: Dict[str, Dict[str, float]] = {

    "GK": {
        "goalkeeping": 0.70,
        "tackling": 0.05,
        "passing": 0.10,
        "shooting": 0.05,
        "fitness": 0.10,
    },

    "LB": {
        "goalkeeping": 0.00,
        "tackling": 0.35,
        "passing": 0.25,
        "shooting": 0.10,
        "fitness": 0.30,
    },

    "CB": {
        "goalkeeping": 0.00,
        "tackling": 0.45,
        "passing": 0.20,
        "shooting": 0.05,
        "fitness": 0.30,
    },

    "RB": {
        "goalkeeping": 0.00,
        "tackling": 0.35,
        "passing": 0.25,
        "shooting": 0.10,
        "fitness": 0.30,
    },

    "DML": {
        "goalkeeping": 0.00,
        "tackling": 0.35,
        "passing": 0.30,
        "shooting": 0.05,
        "fitness": 0.30,
    },

    "DMC": {
        "goalkeeping": 0.00,
        "tackling": 0.35,
        "passing": 0.35,
        "shooting": 0.05,
        "fitness": 0.25,
    },

    "DMR": {
        "goalkeeping": 0.00,
        "tackling": 0.35,
        "passing": 0.30,
        "shooting": 0.05,
        "fitness": 0.30,
    },

    "LM": {
        "goalkeeping": 0.00,
        "tackling": 0.10,
        "passing": 0.35,
        "shooting": 0.20,
        "fitness": 0.35,
    },

    "CM": {
        "goalkeeping": 0.00,
        "tackling": 0.15,
        "passing": 0.45,
        "shooting": 0.10,
        "fitness": 0.30,
    },

    "RM": {
        "goalkeeping": 0.00,
        "tackling": 0.10,
        "passing": 0.35,
        "shooting": 0.20,
        "fitness": 0.35,
    },

    "AML": {
        "goalkeeping": 0.00,
        "tackling": 0.05,
        "passing": 0.30,
        "shooting": 0.35,
        "fitness": 0.30,
    },

    "AMC": {
        "goalkeeping": 0.00,
        "tackling": 0.05,
        "passing": 0.40,
        "shooting": 0.30,
        "fitness": 0.25,
    },

    "AMR": {
        "goalkeeping": 0.00,
        "tackling": 0.05,
        "passing": 0.30,
        "shooting": 0.35,
        "fitness": 0.30,
    },

    "FL": {
        "goalkeeping": 0.00,
        "tackling": 0.05,
        "passing": 0.25,
        "shooting": 0.40,
        "fitness": 0.30,
    },

    "FC": {
        "goalkeeping": 0.00,
        "tackling": 0.05,
        "passing": 0.15,
        "shooting": 0.50,
        "fitness": 0.30,
    },
}


def evaluate_player_v2(
    player: Player,
    position: str,
) -> float:

    position_aliases = {
        "DFL": "LB",
        "DFR": "RB",
        "DFC": "CB",
        "MFL": "LM",
        "MFC": "CM",
        "MFR": "RM",
        "FWC": "FC",
    }

    scoring_position = position_aliases.get(
        position,
        position
    )

    weights = ROLE_WEIGHTS_V2.get(
        scoring_position
    )

    if not weights:
        return 0.0

    # Leggiamo lo stato del giocatore attraverso
    # il nuovo strato Player State.
    #
    # In questa fase non aggiungiamo nuovi malus:
    # effective_skills() gestisce già il morale,
    # mentre fitness entra nei pesi del ruolo.
    state = get_player_state(player)

    if not state.available:
        return 0.0

    skills = effective_skills(
        player,
        position
    )

    values = {
        "goalkeeping": skills.goalkeeping,
        "tackling": skills.tackling,
        "passing": skills.passing,
        "shooting": skills.shooting,
        "fitness": float(state.fitness),
    }

    total = 0.0

    for attribute, weight in weights.items():
        total += values[attribute] * weight

    return total


def player_profile_v2(
    player: Player,
    position: str,
) -> Dict:

    state = get_player_state(player)

    skills = effective_skills(
        player,
        position
    )

    score = evaluate_player_v2(
        player,
        position
    )

    return {
        "player_id": player.player_id,
        "position": position,
        "score": score,
        "effective_skills": {
            "goalkeeping": skills.goalkeeping,
            "tackling": skills.tackling,
            "passing": skills.passing,
            "shooting": skills.shooting,
        },
        "fitness": state.fitness,
        "morale": state.morale,
        "concerns": state.concerns,
        "form": state.form,
        "available": state.available,
    }
