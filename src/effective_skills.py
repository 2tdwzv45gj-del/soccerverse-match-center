from dataclasses import dataclass

from src.models.team import Player
from src.position_engine import compatibility


@dataclass
class EffectiveSkills:
    goalkeeping: float
    tackling: float
    passing: float
    shooting: float

    @property
    def overall(self) -> float:
        return max(
            self.goalkeeping,
            self.tackling,
            self.passing,
            self.shooting,
        )


def morale_multiplier(player: Player) -> float:
    if player.morale <= 0:
        return 0.90

    return 1.00


def effective_skills(
    player: Player,
    requested_position: str,
) -> EffectiveSkills:

    position_factor = compatibility(
        player,
        requested_position
    )

    morale_factor = morale_multiplier(
        player
    )

    factor = position_factor * morale_factor

    return EffectiveSkills(
        goalkeeping=player.rating_gk * factor,
        tackling=player.rating_tackling * factor,
        passing=player.rating_passing * factor,
        shooting=player.rating_shooting * factor,
    )
