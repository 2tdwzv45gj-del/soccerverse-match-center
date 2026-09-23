from typing import Optional

from src.models.team import Player


# Formula status:
# LOCKED:
#   DFC Attacking / Counter / Passing
#   DMC Attacking / Passing
#   MFC Long Ball
#
# STRONGLY CONSOLIDATED:
#   DFC Long Ball
#
# NON LOCKED:
#   tutte le altre combinazioni


def _raw_score(
    position: str,
    style: str,
    tackling: float,
    passing: float,
    shooting: float,
) -> Optional[float]:

    T = tackling
    P = passing
    S = shooting

    formulas = {

        ("DFC", "Attacking"):
            (36*T + 20*P + 16*S) / 40,

        ("DFC", "Counter"):
            (42*T + 20*P + 10*S + 1) / 40,

        ("DFC", "Passing"):
            (38*T + 26*P + 10*S) / 40,

        ("DFC", "Long Ball"):
            (42*T + 18*P + 14*S + 22) / 40,

        ("DMC", "Attacking"):
            (16*T + 32*P + 24*S) / 40,

        ("DMC", "Passing"):
            (15*T + 36*P + 16*S + 11) / 40,

        ("MFC", "Long Ball"):
            (15*T + 40*P + 12*S - 37) / 40,
    }

    return formulas.get((position, style))


def effective_score(
    player: Player,
    position: str,
    style: str,
) -> Optional[float]:
    """
    Calcola l'effective_score reverse-engineered quando
    esiste una formula sufficientemente consolidata.

    Restituisce None quando la combinazione posizione/stile
    non è ancora identificata.

    La compatibility NON viene applicata qui:
    il chiamante deve decidere separatamente se il giocatore
    è utilizzabile nello slot.

    Il fitness viene applicato come fattore percentuale.
    """

    raw = _raw_score(
        position,
        style,
        player.rating_tackling,
        player.rating_passing,
        player.rating_shooting,
    )

    if raw is None:
        return None

    return raw * player.fitness / 100.0
