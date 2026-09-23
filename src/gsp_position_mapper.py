"""GSP position bitmask conversion.

The bit values are the verified Soccerverse position bitmasks
used by the project.
"""

POSITION_BITS = {
    1: "GK",
    2: "LB",
    4: "CB",
    8: "RB",
    16: "DML",
    32: "DMC",
    64: "DMR",
    128: "LM",
    256: "CM",
    512: "RM",
    1024: "AML",
    2048: "AMC",
    4096: "AMR",
    8192: "FL",
    16384: "FC",
    32768: "FR",
}


def decode_position_mask(mask: int) -> list[str]:
    """Decode a Soccerverse position bitmask."""
    if mask <= 0:
        return []

    return [
        name
        for bit, name in POSITION_BITS.items()
        if mask & bit
    ]


def decode_main_position(mask: int) -> str:
    """Decode a single Soccerverse main-position bitmask."""
    positions = decode_position_mask(mask)

    if len(positions) != 1:
        raise ValueError(
            f"Expected one main position, got mask={mask}: "
            f"{positions}"
        )

    return positions[0]
