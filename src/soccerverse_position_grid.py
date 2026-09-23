from typing import Dict, Tuple

from src.soccerverse_position_matrix import (
    SOCCERVERSE_POSITION_MATRIX,
)


# Soccerverse usa "AM" per la posizione centrale
# che nel nostro progetto viene chiamata "AMC".
#
# Le coordinate sono (row, column) nella griglia 9x7.

POSITION_GRID: Dict[str, Tuple[int, int]] = {
    "GK":  (0, 3),

    "LB":  (1, 6),
    "CB":  (1, 3),
    "RB":  (1, 0),

    "DML": (3, 6),
    "DMC": (3, 3),
    "DMR": (3, 0),

    "LM":  (5, 6),
    "CM":  (5, 3),
    "RM":  (5, 0),

    "AML": (7, 6),
    "AMC": (7, 3),
    "AMR": (7, 0),

    "FL":  (8, 6),
    "FC":  (8, 3),
    "FR":  (8, 0),
}


SOURCE_INDEX: Dict[str, int] = {
    "GK": 0,
    "LB": 1,
    "CB": 2,
    "RB": 3,
    "DML": 4,
    "DMC": 5,
    "DMR": 6,
    "LM": 7,
    "CM": 8,
    "RM": 9,
    "AML": 10,
    "AMC": 11,
    "AMR": 12,
    "FL": 13,
    "FC": 14,
    "FR": 15,
}


def soccerverse_penalty(
    source_position: str,
    target_position: str,
) -> int:
    """
    Restituisce la penalità percentuale Soccerverse.

    source_position:
        posizione naturale/principale del giocatore.

    target_position:
        posizione nella quale vogliamo schierarlo.

    Il valore viene letto direttamente dalla matrice ufficiale
    16 x 9 x 7.
    """

    if source_position not in SOURCE_INDEX:
        raise ValueError(
            f"Posizione sorgente non supportata: {source_position}"
        )

    if target_position not in POSITION_GRID:
        raise ValueError(
            f"Posizione target non supportata: {target_position}"
        )

    source_index = SOURCE_INDEX[source_position]

    row, column = POSITION_GRID[target_position]

    return SOCCERVERSE_POSITION_MATRIX[
        source_index
    ][row][column]


def soccerverse_compatibility(
    source_position: str,
    target_position: str,
) -> float:
    """
    Converte la penalità ufficiale in compatibilità [0, 1].
    """

    penalty = soccerverse_penalty(
        source_position,
        target_position,
    )

    return 1.0 - penalty / 100.0
