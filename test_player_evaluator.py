from src.player_evaluator import (
    evaluate_player,
    player_profile,
)
from src.soccerverse_api import SoccerverseAPI
from src.team_loader import create_team


CLUB_ID = 22855
CLUB_NAME = "Rhode Island"


api = SoccerverseAPI()

players_data = api.get_players(
    page=1,
    per_page=100,
    club_id=CLUB_ID
)

team = create_team(
    club_id=CLUB_ID,
    name=CLUB_NAME,
    players_data=players_data["items"]
)


print("===================================")
print(" PLAYER EVALUATOR TEST")
print("===================================")

print()
print("Squadra:", team.name)
print()


for player in team.available_players:

    score = evaluate_player(
        player,
        player.position_main
    )

    print(
        f"{player.player_id:>6} | "
        f"{player.position_main:<3} | "
        f"Rating {player.rating:>2} | "
        f"Role Score {score:.2f}"
    )


print()
print("PROFILO ESEMPIO")
print("-----------------------------------")


example = team.available_players[0]

profile = player_profile(
    example,
    example.position_main
)

print(
    "Giocatore:",
    profile["player_id"]
)

print(
    "Posizione:",
    profile["position"]
)

print(
    "Score:",
    f"{profile['score']:.2f}"
)

print(
    "Attributi:"
)

for attribute, value in profile["attributes"].items():

    print(
        f"  {attribute:<20} {value:.0f}"
    )