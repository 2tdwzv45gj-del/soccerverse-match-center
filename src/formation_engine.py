from typing import Dict, List, Optional

from src.models.team import Player, Team
from src.player_evaluator import evaluate_player
from src.position_engine import compatibility


FORMATIONS = {
    "4-4-2": {
        "GK": 1,
        "LB": 1,
        "CB": 2,
        "RB": 1,
        "LM": 1,
        "CM": 2,
        "RM": 1,
        "FC": 2,
    },

    "4-3-3": {
        "GK": 1,
        "LB": 1,
        "CB": 2,
        "RB": 1,
        "CM": 3,
        "AML": 1,
        "AMR": 1,
        "FC": 1,
    },

    "4-2-3-1": {
        "GK": 1,
        "LB": 1,
        "CB": 2,
        "RB": 1,
        "DMC": 2,
        "AML": 1,
        "AMC": 1,
        "AMR": 1,
        "FC": 1,
    },

    "3-5-2": {
        "GK": 1,
        "CB": 3,
        "LM": 1,
        "CM": 2,
        "RM": 1,
        "DMC": 1,
        "FC": 2,
    },

    "5-3-2": {
        "GK": 1,
        "LB": 1,
        "CB": 3,
        "RB": 1,
        "CM": 2,
        "DMC": 1,
        "FC": 2,
    },
}


def player_base_score(player: Player) -> float:
    """
    Valutazione generale del giocatore.

    Manteniamo questo valore separato dal
    punteggio specifico per ruolo.
    """

    return (
        player.rating * 0.70
        + player.fitness * 0.20
        + player.rating_stamina * 0.10
    )


def candidate_score(
    player: Player,
    position: str,
) -> float:
    """
    Valuta il giocatore nella posizione richiesta.

    Il punteggio specifico del ruolo viene fornito
    dal Player Evaluator.
    """

    position_score = compatibility(
        player,
        position
    )

    if position_score <= 0:
        return 0.0

    role_score = evaluate_player(
        player,
        position
    )

    return role_score * position_score


def build_positions(
    formation: Dict[str, int]
) -> List[str]:

    positions = []

    for position, quantity in formation.items():

        for _ in range(quantity):
            positions.append(position)

    return positions


def get_candidates(
    players: List[Player],
    position: str,
) -> List[Player]:

    candidates = []

    for player in players:

        score = candidate_score(
            player,
            position
        )

        if score > 0:
            candidates.append(player)

    candidates.sort(
        key=lambda player: candidate_score(
            player,
            position
        ),
        reverse=True
    )

    return candidates


def lineup_total_score(
    assignments: List[dict]
) -> float:

    return sum(
        assignment["score"]
        for assignment in assignments
    )


def optimize_assignments(
    positions: List[str],
    players: List[Player],
    index: int = 0,
    used_players: Optional[set] = None,
    current: Optional[List[dict]] = None,
) -> List[dict]:

    if used_players is None:
        used_players = set()

    if current is None:
        current = []

    if index >= len(positions):
        return current

    position = positions[index]

    candidates = get_candidates(
        players,
        position
    )

    # ---------------------------------------------------------------
    # POSIZIONE SCOPERTA
    # ---------------------------------------------------------------

    best_result = optimize_assignments(
        positions,
        players,
        index=index + 1,
        used_players=used_players.copy(),
        current=current + [
            {
                "position": position,
                "player": None,
                "compatibility": 0.0,
                "score": 0.0,
            }
        ],
    )

    best_score = lineup_total_score(
        best_result
    )

    # ---------------------------------------------------------------
    # PROVIAMO I GIOCATORI
    # ---------------------------------------------------------------

    for player in candidates:

        if player.player_id in used_players:
            continue

        position_score = compatibility(
            player,
            position
        )

        score = candidate_score(
            player,
            position
        )

        new_used_players = used_players.copy()
        new_used_players.add(
            player.player_id
        )

        new_current = current + [
            {
                "position": position,
                "player": player,
                "compatibility": position_score,
                "score": score,
            }
        ]

        result = optimize_assignments(
            positions,
            players,
            index=index + 1,
            used_players=new_used_players,
            current=new_current,
        )

        result_score = lineup_total_score(
            result
        )

        if result_score > best_score:
            best_result = result
            best_score = result_score

    return best_result


def find_best_lineup(
    team: Team,
    formation: Dict[str, int],
) -> Dict:

    players = team.available_players

    positions = build_positions(
        formation
    )

    # Prima le posizioni più difficili.
    positions.sort(
        key=lambda position: len(
            get_candidates(
                players,
                position
            )
        )
    )

    assignments = optimize_assignments(
        positions,
        players
    )

    positions_filled = sum(
        1
        for assignment in assignments
        if assignment["player"] is not None
    )

    players_used = len({
        assignment["player"].player_id
        for assignment in assignments
        if assignment["player"] is not None
    })

    adaptations = sum(
        1
        for assignment in assignments
        if (
            assignment["player"] is not None
            and assignment["compatibility"] < 1.0
        )
    )

    missing_positions = sum(
        1
        for assignment in assignments
        if assignment["player"] is None
    )

    if positions_filled > 0:
        quality_score = (
            lineup_total_score(assignments)
            / positions_filled
        )
    else:
        quality_score = 0.0

    completeness = positions_filled / 11

    missing_penalty = missing_positions * 20.0
    adaptation_penalty = adaptations * 2.0

    emergency_penalty = (
        missing_penalty
        + adaptation_penalty
    )

    final_score = (
        quality_score
        + completeness * 20.0
        - emergency_penalty
    )

    if final_score < 0:
        final_score = 0.0

    if missing_positions == 0 and adaptations == 0:
        verdict = "FORMAZIONE COMPLETA"

    elif missing_positions == 0:
        verdict = "FORMAZIONE CON ADATTAMENTI"

    elif positions_filled >= 9:
        verdict = "FORMAZIONE DI EMERGENZA"

    else:
        verdict = "FORMAZIONE FORTEMENTE INCOMPLETA"

    return {
        "assignments": assignments,
        "players_used": players_used,
        "positions_filled": positions_filled,
        "adaptations": adaptations,
        "missing_positions": missing_positions,
        "quality_score": quality_score,
        "completeness": completeness,
        "emergency_penalty": emergency_penalty,
        "final_score": final_score,
        "verdict": verdict,
    }


def analyze_formations(team: Team):

    results = []

    for name, formation in FORMATIONS.items():

        lineup = find_best_lineup(
            team,
            formation
        )

        results.append({
            "name": name,
            "score": lineup["final_score"],
            "lineup": lineup,
        })

    results.sort(
        key=lambda result: (
            result["lineup"]["positions_filled"],
            result["score"],
        ),
        reverse=True
    )

    return results