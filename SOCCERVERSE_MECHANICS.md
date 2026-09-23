# SOCCERVERSE MECHANICS

## SCOPO

Documento di riferimento per distinguere:

- meccaniche verificate;
- meccaniche inferite;
- meccaniche ancora provvisorie.

NON trattare come ufficiale nessuna formula non presente nelle fonti
Soccerverse o non verificata sperimentalmente.

---

# 1. PLAYER RATINGS

## Verificato

Ogni giocatore ha quattro skill:

- Goalkeeping
- Tackling
- Passing
- Shooting

Overall:

    Overall = max(GK, Tackling, Passing, Shooting)

Il rating non è la media delle quattro skill.

Le skill finali sono mantenute nel range 50-99.

---

# 2. ORIGINE DELLE SKILL

## Verificato

Il rating parte dalla forza del club e viene incrementato dagli skill
points derivati dalle prestazioni reali del giocatore.

Le statistiche considerate comprendono:

### Passing

- passes per minute
- key passes per minute
- successful dribbles per minute

### Shooting

- goals per minute
- minutes played
- shots on target per minute
- assists per minute

### Tackling

- duels won percentage
- minutes played
- interceptions per minute
- tackles per minute
- blocks per minute

### Goalkeeping

Per i portieri riconosciuti, principalmente minuti qualificanti
giocati come goalkeeper.

Normalmente servono almeno 300 minuti qualificanti per utilizzare
il calcolo basato sui dati di partita.

---

# 3. NO-DATA ROUTE

## Verificato

Se non ci sono abbastanza dati qualificanti, Soccerverse utilizza:

- club base rating
- età
- posizione

con una matrice età/posizione.

Per un giocatore di movimento:

    GK = 50
    Tackling = club base + adjustment
    Passing = club base + adjustment
    Shooting = club base + adjustment

Per un goalkeeper:

- l'aggiustamento principale riguarda Goalkeeping;
- gli altri skill hanno gli aggiustamenti specifici del goalkeeper.

---

# 4. POSITION ADJUSTMENT

## Verificato

Il sistema controlla se il giocatore viene schierato nella posizione
corretta.

Se è fuori posizione:

- Goalkeeping viene penalizzato;
- Tackling viene penalizzato;
- Passing viene penalizzato;
- Shooting viene penalizzato.

La penalità aumenta quanto più il giocatore è lontano dalla propria
posizione.

Il backend utilizza una matrice:

    g_grid_outta_pos_multi[16][9][7]

## NON ANCORA RICOSTRUITO

La corrispondenza completa tra:

    posizione Soccerverse
    ->
    coordinate della matrice
    ->
    percentuale esatta

non è ancora stata ricostruita integralmente.

Quindi la tabella attuale in:

    src/position_engine.py

è da considerare PROVVISORIA.

NON chiamarla "penalità ufficiale" finché non viene verificata.

---

# 5. MORALE

## Verificato

Il sistema di morale distingue almeno:

- happy
- concerned
- unhappy

I concerns possono derivare, tra le altre cose, da:

- contratto/wage;
- livello della lega;
- minuti giocati.

Il morale viene controllato giornalmente.

## MATCH EFFECT

La documentazione backend indica un modificatore per il giocatore
unhappy.

Il mapping preciso tra i valori API:

    morale=0
    morale=1

e tutti gli stati interni del backend deve essere mantenuto esplicito
nel codice e non interpretato oltre ciò che l'API consente di verificare.

---

# 6. FITNESS

## Verificato

La fitness è considerata dal sistema di scelta dei giocatori.

Durante il match la fitness è collegata alla fatica.

NON deve essere semplicemente trattata come una penalità di posizione.

## STATO ATTUALE

Il nostro player evaluator usa fitness direttamente nel punteggio.

Questo è un MODELLO TATTICO PROVVISORIO, non una formula ufficiale
del match engine.

---

# 7. AUTOPICK

## Verificato

Se la tattica è invalida, il backend può utilizzare l'autopick.

Una tattica è invalida se:

- contiene un giocatore injured;
- contiene un giocatore match banned;
- non contiene un goalkeeper nella posizione GK,

salvo emergenza quando tutti i goalkeeper sono indisponibili.

L'autopick ufficiale sceglie casualmente una tra:

- 4-4-2
- 4-3-3
- 4-5-1

e quindi cerca il miglior giocatore per ogni posizione.

La fitness viene considerata nella scelta.

---

# 8. NOSTRO FORMATION ENGINE

## PROVVISORIO

Il nostro engine analizza:

- 4-4-2
- 4-3-3
- 4-2-3-1
- 3-5-2
- 5-3-2

Questo NON rappresenta ancora l'autopick ufficiale Soccerverse.

È una funzione di ottimizzazione tattica del nostro Tactical Advisor.

Questo è intenzionale.

---

# 9. NOSTRO PLAYER EVALUATOR

## PROVVISORIO

src/player_evaluator_v2.py utilizza pesi per ruolo.

Esempio:

    FC:
        shooting
        passing
        tackling
        fitness

Questi pesi NON sono coefficienti ufficiali Soccerverse.

Servono attualmente a costruire un ranking tattico interno.

---

# 10. NOSTRO EFFECTIVE SKILLS

## PROVVISORIO

Attualmente:

    position_factor = compatibility(...)
    morale_factor = morale_multiplier(...)

    factor = position_factor * morale_factor

e le skill vengono moltiplicate per factor.

Questo modello NON deve essere considerato una replica ufficiale
del match engine.

Il test attuale dimostra soltanto che il nostro prototipo funziona.

Esempio test:

    FC naturale:
        Shooting = 85

    FC -> AMC:
        Shooting = 63.75

Questo risultato deriva dal nostro modello:

    85 * 0.75 = 63.75

Non è ancora una percentuale ufficiale Soccerverse verificata.

---

# 11. PRINCIPIO DI SVILUPPO

Prima di modificare una formula:

1. verificare la fonte;
2. distinguere rating calculation da matchday logic;
3. distinguere posizione da fitness;
4. distinguere morale da concerns;
5. distinguere dati API da interpretazione;
6. aggiungere un test;
7. modificare un solo componente;
8. eseguire py_compile;
9. eseguire i test;
10. testare con almeno due Club ID.

---

# 12. STATO DEL PROGETTO

## VERIFICATO

- API giocatori
- API club name
- Team Loader
- disponibilità
- injured
- banned
- position parsing
- Player model con concerns/form
- Position Engine funzionante come prototipo
- Player Evaluator V2 funzionante come prototipo
- Formation Engine V2 funzionante come prototipo
- main.py dinamico
- Rhode Island test
- Salford test
- Effective Skills test

## DA VERIFICARE

- matrice completa delle penalità posizione
- mapping completo delle coordinate posizione
- formula esatta del match performance
- effetto preciso della fitness nel match
- effetto della form
- effetto morale completo
- tackling style
- tempo
- stamina/fatigue
- relazione tra rating statico e performance durante il match

## NON FARE ANCORA

- Matchup Engine definitivo
- Tactical Advisor definitivo
- coefficienti dichiarati ufficiali
- predizione risultato
- simulazione partita completa

---

# 13. PROSSIMO OBIETTIVO

Ricostruire la matrice posizione ufficiale.

Obiettivo:

    position
       ↓
    official position coordinates
       ↓
    g_grid_outta_pos_multi
       ↓
    penalty %
       ↓
    effective skills

Solo dopo questa fase modificare definitivamente:

    src/position_engine.py
    src/effective_skills.py

---

# 14. FONTI

Soccerverse Wiki:

- Backend Game Logic
- Player Rating Calculation
- Player Morale - Concerns

Le formule non presenti esplicitamente nelle fonti devono essere
marcate come PROVVISORIE o INFERITE.
