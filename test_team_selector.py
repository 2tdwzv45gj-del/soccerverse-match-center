from src.team_selector import select_team


print("===================================")
print(" TEAM SELECTOR TEST")
print("===================================")

team = select_team()

print()
print("SQUADRA SELEZIONATA")
print("-----------------------------------")
print("Club ID:", team["club_id"])