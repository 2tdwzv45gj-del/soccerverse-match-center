# SOCCERVERSE PROJECT STATUS

Last updated: 2026-09-17

---

## CURRENT STATUS

TACTICAL ADVISOR: PAUSED
MATCH COMMENTARY APP: PLANNING

The Tactical Advisor is intentionally paused before GUI completion.
Priority is now to design a separate match-commentary application while
preserving and reusing the Soccerverse data already collected.

---

# WORKSTREAM 1 — TACTICAL ADVISOR

## STATUS

PAUSED — DO NOT CONTINUE GUI WORK UNTIL TACTICAL MODEL IS COMPLETED.

## Product goal

A tactical advisor for up to 5 Soccerverse clubs.

Each club slot may be:
- occupied by a club
- empty

Each occupied club has:
- formation
- play style
- generated XI
- tactical score
- matchup analysis
- recommendation

Maximum: 5 club slots.

---

## LOCKED / VERIFIED

### Position bitmasks

GK=1
LB=2
CB=4
RB=8
DML=16
DMC=32
DMR=64
LM=128
CM=256
RM=512
AML=1024
AMC=2048
AMR=4096
FL=8192
FC=16384
FR=32768

Official Soccerverse position compatibility / penalty model is used.

No heuristic replacement of official position compatibility.

---

## EFFECTIVE SCORE

Implementation exists in:

src/effective_score_engine.py

Validated formulas currently available:

DFC + Attacking
DFC + Counter
DFC + Passing
DFC + Long Ball
DMC + Attacking
DMC + Passing
MFC + Long Ball

Fitness multiplier:

effective_score = raw_score * fitness / 100

Morale is NOT part of effective_score based on current evidence.

Position compatibility is NOT part of effective_score.

DFC Defensive remains OPEN / underdetermined.

Other position/style combinations remain OPEN until sufficient evidence exists.

---

## FORMATIONS

Historical data contains 23 formation IDs:

F0
F1
F2
F3
F4
F5
F6
F7
F8
F10
F11
F12
F13
F14
F15
F16
F17
F18
F19
F20
F21
F22
F23

F9 is absent from current historical inventory.

Currently VERIFIED operational geometries:

F7  = 5-3-2
F11 = 4-1-4-1
F12 = 4-2-3-1
F13 = 4-1-2-2-1v2
F15 = 4-3-1-2
F18 = 1-4-3-2v2
F20 = 4-2-2-2

The catalog is NOT complete.

Do not treat the current 7 formations as the complete Soccerverse formation catalog.

Recent investigation found additional useful evidence in:

data/raw/club_605_formation_slot_patterns.json
data/raw/club_605_formation_slots_analysis.json
data/raw/club_605_teamsheet_formation_analysis.json
data/raw/global_formation_reverse_engineering.json
data/raw/formation_raw_actions_global.json

These have not yet been fully reconciled into VERIFIED geometry.

Next tactical step when resumed:
validate all available formation IDs against slot -> position evidence.

Do NOT invent geometries from formation names.

---

## AUTOPICK

Official GSP autopick_club_tactics was successfully queried for Club 605
for all 23 formation IDs.

Dataset:

data/raw/gsp_autopick/club_605_all_formations.json

23 formation IDs
414 team_sheet entries
23 tactic actions

Autopick changes player selection according to formation.

Historical XI selection has NOT been explained.

Evidence indicates historical lineups are not reproduced by:
- highest rating
- rating * fitness
- rating * compatibility
- current evaluate_player_v2

Autopick reverse engineering remains OPEN.

---

## FORMATION / XI ENGINE

src/formation_engine_v2.py

Uses global assignment architecture / Hungarian assignment.

Current scoring is an advisor heuristic and is NOT claimed to reproduce
Soccerverse internal XI selection.

Controlled regression:
- 11/11 no adaptations -> 100
- 11/11 with 2 adaptations -> 96
- 10/11 -> 78.1818
- 9/11 -> 56.3636
- 8/11 -> 34.5455

These are advisor metrics, not Soccerverse official scores.

---

## MATCHUP

src/matchup_engine.py

Historical matchup evidence exists.

Current dataset contains:
- 92 matchup paths
- 20 unique complete W/D/L combinations in the expanded historical evidence
- larger formation/opponent evidence in real_formation_slot_map_massive.json

Historical results must NOT be interpreted as universal causal
formation/style superiority.

Score orientation in some historical raw fields is not yet reliably established.

---

## API / GSP

Official REST/GSP access has been used successfully.

Known endpoint:

https://play.soccerverse.com/gsp/v1/graph

Current design principle:

CACHE FIRST.

Avoid unnecessary repeated GSP calls.

Do not bypass Cloudflare.
Do not bypass rate limiting.
Do not poll aggressively.

---

# WORKSTREAM 2 — MATCH COMMENTARY APP

## STATUS

PLANNED / DESIGN PHASE

This is a separate application/workstream.

Goal:

Create an attractive GUI application that provides minute-by-minute
Soccerverse match commentary.

The application should reuse existing Soccerverse data wherever useful.

Potential data already available / investigated includes:
- real player names
- player IDs
- club IDs
- squad data
- historical formations
- formation IDs
- play styles
- tactical settings
- lineup information
- team sheets
- historical match data
- opponent information
- player attributes
- fitness
- position compatibility
- effective-score research
- autopick evidence
- GSP access patterns

Important:

The commentary application must distinguish:
LOCKED / VERIFIED data
from
INFERRED / GENERATED commentary.

It must never present speculative tactical interpretation as official
Soccerverse event data.

---

## INITIAL COMMENTARY APP CONCEPT

Live match view should potentially contain:

HOME TEAM
AWAY TEAM
SCORE

MATCH CLOCK

EVENT TIMELINE
- minute
- event
- player
- team
- contextual text

Example generated commentary structure:

12'
PLAYER NAME receives the ball...

15'
PLAYER NAME creates an attacking opportunity...

22'
GOAL — PLAYER NAME

HALF TIME

etc.

Exact event vocabulary and available GSP fields must be established
before implementation.

---

## GUI DIRECTION

Target:

Desktop application with attractive football-match presentation.

Possible layout:

------------------------------------------------
HOME TEAM       2 - 1       AWAY TEAM
                 67'
------------------------------------------------

LIVE EVENT TIMELINE

67'  PLAYER NAME ...
61'  PLAYER NAME ...
54'  SUBSTITUTION ...
45'  HALF TIME
31'  GOAL — PLAYER NAME

------------------------------------------------

MATCH DATA / TACTICS / LINEUPS
------------------------------------------------

The visual design should be modern and useful rather than decorative.

---

## CRITICAL DESIGN RULE

Before implementing commentary generation:

1. Identify the authoritative match-event source.
2. Determine exactly which event fields are available.
3. Determine whether events are historical, live, or both.
4. Determine whether timestamps/minutes are authoritative.
5. Determine which player/club names can be resolved from existing data.
6. Separate official event facts from generated narrative.
7. Only then design the final commentary engine.

---

# REPOSITORY RULES

Use macOS + zsh.

Project root:

~/Desktop/SOCCERVERSE/soccerverse-tactical-advisor

Python executable:

.venv/bin/python

Do NOT use:
python
python3

unless explicitly verified for a specific task.

Prefer ready-to-copy terminal commands.

Avoid manual file editing when a command can safely perform the change.

Keep terminal output compact.

When investigating:
- LOCKED = proven
- VERIFIED = sufficiently evidenced
- OPEN = unresolved
- HYPOTHESIS = plausible but unproven

Never silently promote HYPOTHESIS to VERIFIED.

---

# NEXT SESSION — TACTICAL ADVISOR

When resumed:

1. Complete formation ID -> slot geometry evidence.
2. Validate all 23 formation IDs where evidence permits.
3. Continue effective_score matrix only where data supports it.
4. Reverse engineer official Autopick.
5. Revisit matchup engine.
6. Only then return to tactical GUI.

---

# NEXT SESSION — MATCH COMMENTARY APP

Before coding GUI:

1. Inventory existing match/event data.
2. Identify authoritative Soccerverse match event endpoint/source.
3. Inspect already collected datasets for reusable player/club names.
4. Determine live-event retrieval model.
5. Define event schema.
6. Define commentary generation rules.
7. Design GUI.
8. Implement backend/event pipeline.
9. Implement GUI.
10. Test against real/historical matches.

---

# PRINCIPLE

Prefer a complete, evidence-based product over a rushed incomplete one.


## 2026-09-17 — Match Center: stato consolidato

- Focus attuale: Soccerverse Match Commentary / Match Center; Tactical Advisor in pausa.
- Filosofia: suspense/editorial experience-first. Eventi e minuti ufficiali invariati; replay engine decide il timing, GUI decide presentazione ed effetti.
- Fixture tecnica: 334228 — Vora vs Korçë — 1-0 — gol al 76\x27 di Segerso Geci — Stadiumi Vora — ALB Division 1.
- Dati verificati: 109 sub-eventi commentary, 42 azioni aggregate, 1 gol ufficiale.
- Replay verificato: 3 minuti; inizio 2\x27 0-0; circa 140s 73\x27 0-0; circa 145s 76\x27 1-0; fine 92\x27 1-0.
- Test: 47/47 passati. Composer 6/6, renderer 9/9, replay 11/11, score progression 6/6, replay state 5/5, match data service 4/4, match search 6/6.
- Match Search: ricerca per nome squadra con resolve_club_name e gestione confidence/candidati; Vora verificata con ID 3340, confidence 1.000, 47 match.
- Datapack: data/raw/datapack/rincon_s4.json. Verificati logo Vora, logo Korçë, colori club, Stadiumi Vora e relativa immagine.
- Logo competizione non ancora mappato; decisione: non forzarlo, usare gli asset disponibili.
- GUI: app_match_center/ con PySide6, collegata ai dati reali e al datapack. Avvio: .venv/bin/python -m app_match_center.main.
- GUI già presente: scoreboard dinamico, minuto, momento match, commentary area, replay controls, loghi, colori, stadio e score progressivo.
- Feedback: base GUI approvata; direzione confermata.
- Prossimi step: identità squadra per ogni azione; ReplayScene/ReplayViewState arricchiti con club/player; timeline dinamica; goal cinematic; audio crowd + fischio iniziale/finale; cartellini gialli/rossi; successivamente formazioni, tattiche, statistiche e classifica.
- Goal cinematic concordato: azione → tensione → GOL! → impatto/zoom → bagliore/scia → impulso → 4s respiro → ripresa.
- Principi: niente eventi inventati, niente modifica di ordine/minuto, effetti nella GUI e non nel replay engine, gol come climax, suspense prima della quantità di informazioni.
- Strategia demo: 334228 come technical replay lab; in seguito seconda fixture più iconica/visivamente ricca.
- Stato: base tecnica stabile, GUI promettente e approvata, replay reale funzionante.
