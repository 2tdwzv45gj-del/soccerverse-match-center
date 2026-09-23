def select_team() -> dict:

    print()
    print("===================================")
    print(" SELEZIONE SQUADRA")
    print("===================================")
    print()
    print("Inserisci il Club ID della squadra")
    print("da analizzare.")
    print()

    while True:

        value = input("Club ID: ").strip()

        if not value:
            print("Il Club ID non può essere vuoto.")
            continue

        try:
            club_id = int(value)

        except ValueError:
            print("Inserisci un Club ID numerico.")
            continue

        if club_id <= 0:
            print("Il Club ID deve essere maggiore di zero.")
            continue

        return {
            "club_id": club_id
        }