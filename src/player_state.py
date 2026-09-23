from dataclasses import dataclass

from src.models.team import Player


@dataclass
class PlayerState:
    available: bool
    fitness: int
    morale: int
    concerns: int
    form: str

    @property
    def injured(self) -> bool:
        return self.available is False


def get_player_state(player: Player) -> PlayerState:
    return PlayerState(
        available=player.is_available,
        fitness=player.fitness,
        morale=player.morale,
        concerns=player.concerns,
        form=player.form,
    )


def describe_player_state(player: Player) -> str:
    state = get_player_state(player)

    if not state.available:
        return "NON DISPONIBILE"

    if state.morale == 1 and state.concerns == 0:
        morale_state = "normale"
    elif state.morale == 0 and state.concerns > 0:
        morale_state = "con concerns"
    else:
        morale_state = "stato morale da verificare"

    return (
        f"disponibile | "
        f"fitness {state.fitness} | "
        f"morale {morale_state} | "
        f"concerns {state.concerns} | "
        f"form {state.form}"
    )
