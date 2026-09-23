from src.commentary_composer import NarrativeIntent
from src.commentary_renderer import render_narrative


def intent(
    kind,
    primary=None,
    secondary=None,
    supporting=None,
    goalkeeper=None,
    minute=5,
):
    return NarrativeIntent(
        action_id=100,
        minute=minute,
        kind=kind,
        creator_player=primary,
        shooter_player=secondary,
        defender_player=supporting,
        goalkeeper=goalkeeper,
        substitute_on=primary if kind == "substitution" else None,
        substitute_off=secondary if kind == "substitution" else None,
        club_name="Club",
    )


def test_saved_chance():
    text = render_narrative(
        intent(
            "chance_saved",
            primary="Jurgen Vrapi",
            secondary="Patrik Bardhi",
            goalkeeper="Marco Alia",
        )
    )

    assert text == "Vrapi serve Bardhi, che conclude: Alia para."


def test_saved_chance_without_assist():
    text = render_narrative(
        intent(
            "chance_saved",
            primary="Ionuț Albu",
            goalkeeper="Marco Alia",
        )
    )

    assert text == "Albu conclude, ma Alia para."


def test_offtarget_chance():
    text = render_narrative(
        intent(
            "chance_offtarget",
            primary="Ionuț Albu",
            secondary="Patrik Bardhi",
        )
    )

    assert text == "Albu serve Bardhi, che conclude fuori bersaglio."


def test_offtarget_single_player():
    text = render_narrative(
        intent(
            "chance_offtarget",
            primary="Patrik Bardhi",
        )
    )

    assert text == "Bardhi conclude fuori bersaglio."


def test_tackle():
    text = render_narrative(
        intent(
            "chance_tackled",
            primary="Manfredas Ruzgis",
            secondary="Odirah Ntephe",
            supporting="Alcides Javier Valdez Torres",
        )
    )

    assert text == "Ntephe serve Ruzgis, ma Valdez Torres chiude l'azione."


def test_tackle_without_assist():
    text = render_narrative(
        intent(
            "chance_tackled",
            primary="Ardit Nikaj",
            supporting="Dajan Shehi",
        )
    )

    assert text == "Nikaj cerca spazio, ma Shehi interrompe l'azione."


def test_substitution():
    text = render_narrative(
        intent(
            "substitution",
            primary="Nikolin Duka",
            secondary="Eni Imami",
        )
    )

    assert text == "Entra Duka, esce Imami."


def test_goal():
    text = render_narrative(
        intent(
            "goal",
            primary="Segerso Geci",
            minute=76,
        )
    )

    assert text == "76' GOL! Geci trova la rete."


def test_player_name_is_rendered_as_surname():
    text = render_narrative(
        intent(
            "goal",
            primary="Benjamín Gonzalo Guzmán Pérez",
            minute=43,
        )
    )

    assert text == "43' GOL! Guzmán Pérez trova la rete."
