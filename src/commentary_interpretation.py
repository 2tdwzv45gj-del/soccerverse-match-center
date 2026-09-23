from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .commentary_actions import CommentaryAction


class ActionKind(str, Enum):
    CHANCE = "chance"
    SHOT = "shot"
    SAVE = "save"
    OFFTARGET = "offtarget"
    TACKLE = "tackle"
    SUBSTITUTION = "substitution"
    GOAL = "goal"
    OTHER = "other"


CATEGORY_TO_KIND: dict[str, ActionKind] = {
    "ASSISTEDCHANCE": ActionKind.CHANCE,
    "CHANCE": ActionKind.CHANCE,
    "SHOT": ActionKind.SHOT,
    "SAVE": ActionKind.SAVE,
    "OFFTARGET": ActionKind.OFFTARGET,
    "TACKLE": ActionKind.TACKLE,
    "SUB": ActionKind.SUBSTITUTION,
    "GOAL": ActionKind.GOAL,
}


@dataclass(frozen=True)
class InterpretedAction:
    action: CommentaryAction
    kind: ActionKind
    primary_player_id: int | None
    secondary_player_id: int | None

    @property
    def minute(self) -> int:
        return self.action.time

    @property
    def club_id(self) -> int | None:
        return self.action.club_one_id

    @property
    def club_name(self) -> str | None:
        return self.action.club_one_name


def interpret_action(action: CommentaryAction) -> InterpretedAction:
    categories = action.categories

    kind = ActionKind.OTHER

    for category in categories:
        mapped = CATEGORY_TO_KIND.get(category)
        if mapped is not None:
            # GOAL takes precedence over the supporting commentary chain.
            if mapped == ActionKind.GOAL:
                kind = mapped
                break
            if kind == ActionKind.OTHER:
                kind = mapped

    player_ids = action.player_ids

    primary = player_ids[0] if player_ids else None
    secondary = player_ids[1] if len(player_ids) > 1 else None

    return InterpretedAction(
        action=action,
        kind=kind,
        primary_player_id=primary,
        secondary_player_id=secondary,
    )


def interpret_actions(
    actions: tuple[CommentaryAction, ...],
) -> tuple[InterpretedAction, ...]:
    return tuple(interpret_action(action) for action in actions)
