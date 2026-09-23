from __future__ import annotations

from dataclasses import dataclass

from src.commentary_actions import CommentaryAction


@dataclass(frozen=True)
class NarrativeIntent:
    action_id: int
    minute: int
    kind: str

    # Ruoli narrativi espliciti.
    # creator_player = chi crea/serve l'azione
    # shooter_player = chi conclude
    # defender_player = chi interrompe con un tackle
    creator_player: str | None
    shooter_player: str | None
    defender_player: str | None
    goalkeeper: str | None
    substitute_on: str | None
    substitute_off: str | None

    creator_player_id: int | None
    shooter_player_id: int | None
    defender_player_id: int | None
    goalkeeper_id: int | None
    substitute_on_id: int | None
    substitute_off_id: int | None

    club_name: str | None


def _find_player_one(
    action: CommentaryAction,
    category: str,
) -> str | None:
    for event in action.sub_events:
        if event.category == category:
            return event.player_one_name
    return None


def _find_player_two(
    action: CommentaryAction,
    category: str,
) -> str | None:
    for event in action.sub_events:
        if event.category == category:
            return event.player_two_name
    return None


def _find_player_one_id(
    action: CommentaryAction,
    category: str,
) -> int | None:
    for event in action.sub_events:
        if event.category == category:
            return event.player_one_id
    return None


def _find_player_two_id(
    action: CommentaryAction,
    category: str,
) -> int | None:
    for event in action.sub_events:
        if event.category == category:
            return event.player_two_id
    return None


def compose_action(action: CommentaryAction) -> NarrativeIntent:
    categories = action.categories

    creator = None
    shooter = None
    defender = None
    goalkeeper = None
    substitute_on = None
    substitute_off = None

    if "GOAL" in categories:
        kind = "goal"

        creator = _find_player_one(action, "CHANCE")
        shooter = _find_player_one(action, "GOAL")

        if shooter is None:
            shooter = _find_player_one(action, "SHOT")

        if shooter is None:
            shooter = creator

    elif "SAVE" in categories:
        kind = "chance_saved"

        creator = _find_player_one(action, "ASSISTEDCHANCE")
        shooter = _find_player_two(action, "ASSISTEDCHANCE")

        if shooter is None:
            shooter = _find_player_one(action, "SHOT")

        if shooter is None:
            shooter = _find_player_one(action, "CHANCE")

        goalkeeper = _find_player_one(action, "SAVE")

    elif "OFFTARGET" in categories:
        kind = "chance_offtarget"

        creator = _find_player_one(action, "ASSISTEDCHANCE")
        shooter = _find_player_two(action, "ASSISTEDCHANCE")

        if shooter is None:
            shooter = _find_player_one(action, "SHOT")

        if shooter is None:
            shooter = _find_player_one(action, "CHANCE")

    elif "TACKLE" in categories:
        kind = "chance_tackled"

        creator = _find_player_one(action, "ASSISTEDCHANCE")
        shooter = _find_player_two(action, "ASSISTEDCHANCE")

        defender = _find_player_one(action, "TACKLE")

        if shooter is None:
            shooter = _find_player_one(action, "CHANCE")

    elif "SUB" in categories:
        kind = "substitution"

        # Nei dati ufficiali:
        # player_one = entrante
        # player_two = uscente
        substitute_on = _find_player_one(action, "SUB")
        substitute_off = _find_player_two(action, "SUB")

    elif "SHOT" in categories:
        kind = "shot"
        shooter = _find_player_one(action, "SHOT")

    else:
        kind = "other"

    return NarrativeIntent(
        action_id=action.comm_event_id,
        minute=action.time,
        kind=kind,
        creator_player=creator,
        shooter_player=shooter,
        defender_player=defender,
        goalkeeper=goalkeeper,
        substitute_on=substitute_on,
        substitute_off=substitute_off,

        creator_player_id=_find_player_one_id(action, "ASSISTEDCHANCE")
        or _find_player_one_id(action, "CHANCE"),

        shooter_player_id=_find_player_one_id(action, "GOAL")
        or _find_player_two_id(action, "ASSISTEDCHANCE")
        or _find_player_one_id(action, "SHOT")
        or _find_player_one_id(action, "CHANCE"),

        defender_player_id=_find_player_one_id(action, "TACKLE"),

        goalkeeper_id=_find_player_one_id(action, "SAVE"),

        substitute_on_id=_find_player_one_id(action, "SUB"),

        substitute_off_id=_find_player_two_id(action, "SUB"),

        club_name=action.club_one_name,
    )


def compose_actions(
    actions: tuple[CommentaryAction, ...],
) -> tuple[NarrativeIntent, ...]:
    return tuple(compose_action(action) for action in actions)
