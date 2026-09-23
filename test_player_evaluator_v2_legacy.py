from src.models.team import Player
from src.player_evaluator_v2 import evaluate_player_v2


player = Player(
    player_id=1,
    position_main="FC",
    positions=["FC"],
    rating=80,
    rating_gk=10,
    rating_tackling=30,
    rating_passing=60,
    rating_shooting=90,
    rating_stamina=80,
    rating_aggression=60,
    fitness=100,
    morale=1,
    concerns=0,
    form="666666",
    injured=0,
    banned=0,
    age=25,
)


natural_score = evaluate_player_v2(
    player,
    "FC"
)

adapted_score = evaluate_player_v2(
    player,
    "AMC"
)


assert natural_score > adapted_score
assert natural_score > 0
assert adapted_score > 0


print("PLAYER EVALUATOR V2")
print("-----------------------------------")
print(
    f"FC naturale : "
    f"{natural_score:.2f}"
)
print(
    f"AMC adattato: "
    f"{adapted_score:.2f}"
)

print()
print("OK - Player Evaluator V2")
