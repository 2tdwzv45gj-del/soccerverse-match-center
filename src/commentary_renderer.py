from __future__ import annotations

import re

from src.commentary_composer import NarrativeIntent


def _surname(name: str | None) -> str | None:
    if not name:
        return None

    parts = name.strip().split()
    if not parts:
        return None

    # Regola V1:
    # 1-2 parole -> ultima parola
    # 3 parole -> ultima parola (da verificare sui dati reali)
    # 4+ parole -> ultime due, per gestire cognomi composti
    # "Jurgen Vrapi" -> "Vrapi"
    # "Benjamín Gonzalo Guzmán Pérez" -> "Guzmán Pérez"
    if len(parts) >= 4:
        return " ".join(parts[-2:])

    return parts[-1]


def render_narrative(intent: NarrativeIntent) -> str:
    primary = _surname(intent.creator_player)
    secondary = _surname(intent.shooter_player)
    supporting = _surname(intent.defender_player)
    goalkeeper = _surname(intent.goalkeeper)
    substitute_on = _surname(intent.substitute_on)
    substitute_off = _surname(intent.substitute_off)

    if intent.kind == "chance_saved":
        if primary and secondary and goalkeeper:
            return f"{primary} serve {secondary}, che conclude: {goalkeeper} para."

        if primary and goalkeeper:
            return f"{primary} conclude, ma {goalkeeper} para."

        if goalkeeper:
            return f"Conclusione: {goalkeeper} para."

        if primary:
            return f"{primary} conclude."

        return "Occasione neutralizzata."

    if intent.kind == "chance_offtarget":
        if primary and secondary:
            return f"{primary} serve {secondary}, che conclude fuori bersaglio."

        if primary:
            return f"{primary} conclude fuori bersaglio."

        return "Conclusione fuori bersaglio."

    if intent.kind == "chance_tackled":
        if secondary and primary and supporting:
            return f"{secondary} serve {primary}, ma {supporting} chiude l'azione."

        if primary and supporting:
            return f"{primary} cerca spazio, ma {supporting} interrompe l'azione."

        if supporting:
            return f"{supporting} interrompe l'azione."

        if primary:
            return f"{primary} cerca spazio."

        return "Azione interrotta."

    if intent.kind == "substitution":
        if substitute_on and substitute_off:
            return f"Entra {substitute_on}, esce {substitute_off}."

        if substitute_on:
            return f"Entra {substitute_on}."

        if substitute_off:
            return f"Esce {substitute_off}."

        return "Sostituzione."

    if intent.kind == "goal":
        if primary:
            return f"{intent.minute}' GOL! {primary} trova la rete."

        return f"{intent.minute}' GOL!"

    if intent.kind == "shot":
        if primary:
            return f"{primary} conclude."

        return "Conclusione."

    if intent.kind == "chance":
        if primary and secondary:
            return f"{primary} serve {secondary}."

        if primary:
            return f"Occasione per {primary}."

        return "Occasione."

    if intent.kind == "save":
        if goalkeeper:
            return f"Parata di {goalkeeper}."

        return "Parata."

    if intent.kind == "offtarget":
        if primary:
            return f"{primary} conclude fuori bersaglio."

        return "Conclusione fuori bersaglio."

    if intent.kind == "tackle":
        if supporting:
            return f"{supporting} interviene."

        return "Intervento difensivo."

    return "Azione al {}° minuto.".format(intent.minute)
