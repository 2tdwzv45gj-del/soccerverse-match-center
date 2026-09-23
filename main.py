from src.formation_engine_v2 import analyze_formations
from src.position_engine import explain_compatibility
from src.soccerverse_api import SoccerverseAPI
from src.team_loader import create_team


print("===================================")
print(" SOCCERVERSE TACTICAL ADVISOR")
print("===================================")

print()
club_id_input = input("Inserisci il Club ID: ").strip()

if not club_id_input.isdigit():
    print("Errore: il Club ID deve essere un numero.")
    raise SystemExit(1)

club_id = int(club_id_input)


print()
style_input = input(
    "Inserisci il Play Style (vuoto = neutro): "
).strip()

STYLE_MAP = {
    "normal": "Normal",
    "defensive": "Defensive",
    "attacking": "Attacking",
    "passing": "Passing",
    "counter": "Counter",
    "long ball": "Long Ball",
    "longball": "Long Ball",
}

style = STYLE_MAP.get(style_input.lower())

if style_input and style is None:
    print(
        "Play Style non riconosciuto. "
        "Usare: Normal, Defensive, Attacking, Passing, Counter, Long Ball."
    )
    raise SystemExit(1)


api = SoccerverseAPI()


players_data = api.get_players(
    page=1,
    per_page=100,
    club_id=club_id
)


if not players_data.get("items"):
    print()
    print("Nessun giocatore trovato per questo Club ID.")
    raise SystemExit(1)


team_name = api.get_club_name(club_id)

if not team_name:
    team_name = f"Club {club_id}"


team = create_team(
    club_id=club_id,
    name=team_name,
    players_data=players_data["items"]
)


results = analyze_formations(team, style=style)


if not results:
    print()
    print("Impossibile analizzare le formazioni.")
    raise SystemExit(1)


print()
print("Squadra:", team.name)
print("Club ID:", team.club_id)
print("Rosa:", len(team.players))
print("Disponibili:", len(team.available_players))
print("Infortunati:", len(team.injured_players))
print("Squalificati:", len(team.banned_players))

print()
print("CLASSIFICA MODULI")
print("-----------------------------------")

for index, result in enumerate(
    results,
    start=1
):

    lineup = result["lineup"]

    print(
        f"{index}. "
        f"{result['name']:<8} "
        f"Score: {result['score']:.2f} | "
        f"Copertura: "
        f"{lineup['positions_filled']}/11 | "
        f"Adattamenti: "
        f"{lineup['adaptations']} | "
        f"Scoperte: "
        f"{lineup['missing_positions']}"
    )


best = results[0]


print()
print("MIGLIOR CONFIGURAZIONE")
print("-----------------------------------")

print(
    f"Modulo: {best['name']}"
)

print(
    f"Verdetto: "
    f"{best['lineup']['verdict']}"
)

print(
    f"Score finale: "
    f"{best['score']:.2f}"
)

print(
    f"Qualità giocatori: "
    f"{best['lineup']['quality_score']:.2f}"
)

print(
    f"Copertura: "
    f"{best['lineup']['positions_filled']}/11"
)

print(
    f"Adattamenti: "
    f"{best['lineup']['adaptations']}"
)

print(
    f"Posizioni scoperte: "
    f"{best['lineup']['missing_positions']}"
)

print()
print("FORMAZIONE")
print("-----------------------------------")

for assignment in best["lineup"]["assignments"]:

    position = assignment["position"]
    player = assignment["player"]

    if player is None:

        print(
            f"{position:<3} | "
            f"NESSUN GIOCATORE"
        )

        continue

    explanation = explain_compatibility(
        player,
        position
    )

    print(
        f"{position:<3} | "
        f"{player.player_id:>6} | "
        f"Rating {player.rating:>2} | "
        f"Fitness {player.fitness:>3} | "
        f"{explanation}"
    )