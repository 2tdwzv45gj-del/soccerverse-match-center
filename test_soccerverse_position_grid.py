from src.soccerverse_position_matrix import SOCCERVERSE_POSITION_MATRIX

GRID_POSITIONS = {
    "GK": (0, 3),
    "RB": (1, 0), "CB": (1, 3), "LB": (1, 6),
    "DMR": (3, 0), "DMC": (3, 3), "DML": (3, 6),
    "RM": (5, 0), "CM": (5, 3), "LM": (5, 6),
    "AMR": (7, 0), "AM": (7, 3), "AML": (7, 6),
    "FR": (8, 0), "FC": (8, 3), "FL": (8, 6),
}

SOURCE_INDEX = {
    "GK": 0, "LB": 1, "CB": 2, "RB": 3,
    "DML": 4, "DMC": 5, "DMR": 6,
    "LM": 7, "CM": 8, "RM": 9,
    "AML": 10, "AM": 11, "AMR": 12,
    "FL": 13, "FC": 14, "FR": 15,
}

def test_natural_positions_have_zero_penalty():
    for position, (row, col) in GRID_POSITIONS.items():
        source = SOURCE_INDEX[position]
        penalty = SOCCERVERSE_POSITION_MATRIX[source][row][col]
        assert penalty == 0, f"{position}: expected 0, got {penalty}"
