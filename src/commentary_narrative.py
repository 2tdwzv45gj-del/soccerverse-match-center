from __future__ import annotations

from dataclasses import dataclass

from .commentary_interpretation import ActionKind, InterpretedAction


@dataclass(frozen=True)
class Narrative:
    minute: int
    text: str
    source_action_id: int


def _player_name(action: InterpretedAction) -> str:
    for event in action.action.sub_events:
        if event.player_one_id == action.primary_player_id:
            if event.player_one_name:
                return event.player_one_name

    return "Un giocatore"


def _secondary_player_name(action: InterpretedAction) -> str | None:
    if action.secondary_player_id is None:
        return None

    for event in action.action.sub_events:
        if event.player_two_id == action.secondary_player_id:
            return event.player_two_name

    return None


def generate_narrative(action: InterpretedAction) -> Narrative:
    player = _player_name(action)
    secondary = _secondary_player_name(action)

    if action.kind == ActionKind.GOAL:
        text = f"⚽ Gol di {player}."

    elif action.kind == ActionKind.SAVE:
        text = f"🧤 Parata di {player}."

    elif action.kind == ActionKind.SHOT:
        text = f"🎯 Conclusione di {player}."

    elif action.kind == ActionKind.OFFTARGET:
        text = f"Conclusione di {player} fuori bersaglio."

    elif action.kind == ActionKind.TACKLE:
        text = f"Contrasto di {player}."

    elif action.kind == ActionKind.CHANCE:
        if secondary:
            text = f"Occasione: {player} serve {secondary}."
        else:
            text = f"Occasione per {player}."

    elif action.kind == ActionKind.SUBSTITUTION:
        if secondary:
            text = f"Sostituzione: {player} per {secondary}."
        else:
            text = "Sostituzione."

    else:
        text = f"Azione al {action.minute}° minuto."

    return Narrative(
        minute=action.minute,
        text=text,
        source_action_id=action.action.comm_event_id,
    )


def generate_narratives(
    actions: tuple[InterpretedAction, ...],
) -> tuple[Narrative, ...]:
    return tuple(generate_narrative(action) for action in actions)
