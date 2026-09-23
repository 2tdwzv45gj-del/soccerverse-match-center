from src.soccerverse_api import SoccerverseAPI
from src.team_loader import create_team
from src.formation_engine import analyze_formations as analyze_v1
from src.formation_engine_v2 import analyze_formations as analyze_v2


CLUBS = [
    22855,
    1844,
]


def load_team(api, club_id):

    players_data = api.get_players(
        page=1,
        per_page=100,
        club_id=club_id
    )

    if not players_data.get("items"):
        raise RuntimeError(
            f"Nessun giocatore trovato per Club ID {club_id}"
        )

    return create_team(
        club_id=club_id,
        name=f"Club {club_id}",
        players_data=players_data["items"]
    )


api = SoccerverseAPI()


for club_id in CLUBS:

    print()
    print("===================================")
    print(f" CLUB ID {club_id}")
    print("===================================")

    team = load_team(
        api,
        club_id
    )

    print(
        f"Rosa: {len(team.players)} | "
        f"Disponibili: {len(team.available_players)} | "
        f"Infortunati: {len(team.injured_players)} | "
        f"Squalificati: {len(team.banned_players)}"
    )

    results_v1 = analyze_v1(team)
    results_v2 = analyze_v2(team)

    best_v1 = results_v1[0]
    best_v2 = results_v2[0]

    print()
    print("V1")
    print("-----------------------------------")
    print(
        f"Modulo: {best_v1['name']} | "
        f"Score: {best_v1['score']:.2f} | "
        f"Copertura: "
        f"{best_v1['lineup']['positions_filled']}/11 | "
        f"Adattamenti: "
        f"{best_v1['lineup']['adaptations']}"
    )

    print()
    print("V2")
    print("-----------------------------------")
    print(
        f"Modulo: {best_v2['name']} | "
        f"Score: {best_v2['score']:.2f} | "
        f"Copertura: "
        f"{best_v2['lineup']['positions_filled']}/11 | "
        f"Adattamenti: "
        f"{best_v2['lineup']['adaptations']}"
    )

    print()
    print("CONFRONTO")
    print("-----------------------------------")

    if best_v1["name"] == best_v2["name"]:
        print("Modulo scelto: UGUALE")
    else:
        print(
            f"Modulo cambiato: "
            f"{best_v1['name']} -> {best_v2['name']}"
        )

    if (
        best_v1["lineup"]["positions_filled"]
        == best_v2["lineup"]["positions_filled"]
    ):
        print("Copertura: UGUALE")
    else:
        print(
            "Copertura cambiata: "
            f"{best_v1['lineup']['positions_filled']}/11 "
            "-> "
            f"{best_v2['lineup']['positions_filled']}/11"
        )
