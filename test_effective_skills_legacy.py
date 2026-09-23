from src.models.team import Player
from src.effective_skills import effective_skills


player = Player(
    player_id=1,
    position_main="FC",
    positions=["FC"],
    rating=80,
    rating_gk=10,
    rating_tackling=35,
    rating_passing=70,
    rating_shooting=85,
    rating_stamina=80,
    rating_aggression=60,
    fitness=100,
    morale=100,
    concerns=0,
    form="666666",
    injured=0,
    banned=0,
    age=25,
)


natural = effective_skills(
    player,
    "FC",
)

adapted = effective_skills(
    player,
    "AMC",
)


print("EFFECTIVE SKILLS TEST")
print("-----------------------------------")

print("POSIZIONE NATURALE")
print(f"GK:       {natural.goalkeeping:.2f}")
print(f"Tackling: {natural.tackling:.2f}")
print(f"Passing:  {natural.passing:.2f}")
print(f"Shooting: {natural.shooting:.2f}")
print(f"Overall:  {natural.overall:.2f}")

print()
print("POSIZIONE ADATTATA")
print(f"GK:       {adapted.goalkeeping:.2f}")
print(f"Tackling: {adapted.tackling:.2f}")
print(f"Passing:  {adapted.passing:.2f}")
print(f"Shooting: {adapted.shooting:.2f}")
print(f"Overall:  {adapted.overall:.2f}")


assert natural.goalkeeping == 10
assert natural.tackling == 35
assert natural.passing == 70
assert natural.shooting == 85
assert natural.overall == 85

assert adapted.goalkeeping <= natural.goalkeeping
assert adapted.tackling <= natural.tackling
assert adapted.passing <= natural.passing
assert adapted.shooting <= natural.shooting
assert adapted.overall <= natural.overall


print()
print("OK - Effective Skills")
