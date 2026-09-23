"use client";

import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import styles from "./page.module.css";
import {
  MatchReplayController,
  type MatchReplayData,
  type ReplayViewState,
} from "@/lib/replay/matchReplayController";

type Match = {
  fixtureId: number;
  homeClubId: number;
  awayClubId: number;
  home: { id: number; name: string; logo: string | null; colors: number[] | null };
  away: { id: number; name: string; logo: string | null; colors: number[] | null };
  homeGoals: number;
  awayGoals: number;
  played: boolean;
  datetime: string;
  competition: string;
};

type MatchDetail = Match & {
  stadium: { id: number; name: string; image: string } | null;
  events: Array<Record<string, any>>;
  commentary: Array<Record<string, any>>;
};

type ReplayEntry = {
  match: MatchDetail;
  controller: MatchReplayController;
  kickoffMs: number;
};

function parseDate(value: string) {
  const normalized = String(value || "").replace(" ", "T");
  const timestamp = Date.parse(normalized);
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function formatDate(value: string) {
  const timestamp = parseDate(value);
  if (!timestamp) return value;
  return new Intl.DateTimeFormat("it-IT", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(timestamp));
}

function formatTime(value: string) {
  const timestamp = parseDate(value);
  if (!timestamp) return "";
  return new Intl.DateTimeFormat("it-IT", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp));
}

function formatGlobalTime(seconds: number) {
  const total = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(total / 60);
  const secs = total % 60;
  return String(minutes).padStart(2, "0") + ":" + String(secs).padStart(2, "0");
}

function buildReplayData(match: MatchDetail): MatchReplayData {
  return {
    fixture: {
      home_club: Number(match.homeClubId),
      away_club: Number(match.awayClubId),
      home_club_name: match.home.name,
      away_club_name: match.away.name,
    },
    events: match.events.map((event) => ({
      event_type: event.event_type,
      time: Number(event.time ?? event.time_minutes ?? 0),
      club_id: event.club_id ?? null,
      player_id: event.player_id ?? null,
      event_player_id: event.event_player_id ?? null,
      match_event_id: event.match_event_id ?? null,
    })),
    commentary: match.commentary.map((event) => ({
      comm_sub_event_id: Number(event.comm_sub_event_id),
      comm_event_id: Number(event.comm_event_id),
      time: Number(event.time),
      category: String(event.category ?? ""),
      player_one_id: event.player_one_id ?? null,
      player_one_name: event.player_one_name ?? null,
      player_two_id: event.player_two_id ?? null,
      player_two_name: event.player_two_name ?? null,
      club_one_id: event.club_one_id ?? null,
      club_one_name: event.club_one_name ?? null,
    })),
  };
}

function teamColor(team: MatchDetail["home"]) {
  return team.colors?.length === 3
    ? "rgb(" + team.colors.join(",") + ")"
    : "rgba(255,255,255,0.18)";
}

function eventIcon(kind: string) {
  if (kind === "goal") return "⚽";
  if (kind === "substitution") return "🔄";
  if (kind === "chance_saved") return "🧤";
  if (kind === "chance_offtarget") return "🎯";
  if (kind === "chance_tackled") return "🛡️";
  if (kind === "shot") return "🎯";
  return "•";
}

function MatchCard({
  entry,
  state,
  globalElapsed,
}: {
  entry: ReplayEntry;
  state: ReplayViewState;
  globalElapsed: number;
}) {
  const match = entry.match;
  const waiting = match.played !== true;
  const finished =
    match.played === true &&
    globalElapsed >= entry.controller.durationSeconds;

  const currentScenes = state.visible_scenes.slice(-3);

  return (
    <article
      className={
        styles.card + (finished ? " " + styles.finishedCard : "")
      }
      onClick={() => {
        if (finished) {
          window.location.href = "/match/" + match.fixtureId;
        }
      }}
      onKeyDown={(event) => {
        if (
          finished &&
          (event.key === "Enter" || event.key === " ")
        ) {
          event.preventDefault();
          window.location.href = "/match/" + match.fixtureId;
        }
      }}
      role={finished ? "link" : undefined}
      tabIndex={finished ? 0 : undefined}
      style={{
        borderColor: waiting
          ? "rgba(255,255,255,0.08)"
          : "rgba(85,194,255,0.28)",
      }}
    >
      {finished === false && (
        <>
          <div className={styles.cardTop}>
            <span>
              {formatDate(match.datetime)} · {formatTime(match.datetime)}
            </span>
            <span>{match.competition || "SOCCERVERSE"}</span>
          </div>

          <div className={styles.statusRow}>
            <span className={waiting ? styles.waiting : styles.live}>
              {waiting ? "● NEXT MATCH" : "● LIVE REPLAY"}
            </span>
            <span>
              {waiting
                ? "Kick-off " + formatTime(match.datetime)
                : state.match_minute + "'"}
            </span>
          </div>
        </>
      )}

      <div className={styles.teams}>
        <div className={styles.team}>
          <div className={styles.logoBox}>
            {match.home.logo ? (
              <img src={match.home.logo} alt="" />
            ) : (
              <span>⚽</span>
            )}
          </div>
          <strong>{match.home.name}</strong>
        </div>

        <div className={styles.score}>
          <strong>{waiting ? "—" : state.home_score}</strong>
          <span>−</span>
          <strong>{waiting ? "—" : state.away_score}</strong>
        </div>

        <div className={styles.team}>
          <div className={styles.logoBox}>
            {match.away.logo ? (
              <img src={match.away.logo} alt="" />
            ) : (
              <span>⚽</span>
            )}
          </div>
          <strong>{match.away.name}</strong>
        </div>
      </div>

      {finished === false && (
        <div className={styles.meta}>
          <span>🏟️ {match.stadium?.name || "Stadium"}</span>
        </div>
      )}

      {waiting === false &&
        finished === false &&
        currentScenes.length > 0 && (
          <div className={styles.events}>
            {currentScenes.map((scene, index) => (
              <div
                className={styles.event}
                key={
                  String(scene.scene.action_id) +
                  "-" +
                  String(index)
                }
              >
                <span>{scene.scene.match_minute}&apos;</span>
                <b>{eventIcon(scene.scene.kind)}</b>
                <span>
                  {scene.scene.player_name ||
                    scene.scene.kind.replaceAll("_", " ")}
                </span>
                {scene.scene.club_name && (
                  <small>{scene.scene.club_name}</small>
                )}
              </div>
            ))}
          </div>
        )}
    </article>
  );
}
function MultiplexContent() {
  const searchParams = useSearchParams();
  const clubIdsParam = searchParams.get("clubIds");

  const [clubIds, setClubIds] = useState<number[]>([]);
  const [matches, setMatches] = useState<MatchDetail[]>([]);
  const [states, setStates] = useState<ReplayViewState[]>([]);
  const [globalElapsed, setGlobalElapsed] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [playing, setPlaying] = useState(false);

  const animationRef = useRef<number | null>(null);
  const lastTimestampRef = useRef<number | null>(null);
  const globalElapsedRef = useRef(0);

  useEffect(() => {
    const fromUrl = (clubIdsParam || "")
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((id) => Number.isInteger(id) && id > 0);

    if (fromUrl.length > 0) {
      setClubIds(fromUrl.slice(0, 10));
      return;
    }

    try {
      const raw = window.localStorage.getItem("sv-live-score-favorites");
      const favorites = raw ? JSON.parse(raw) : [];
      const ids = Array.isArray(favorites)
        ? favorites
            .map((value) => Number(value))
            .filter((id) => Number.isInteger(id) && id > 0)
        : [];
      setClubIds(ids.slice(0, 10));
    } catch {
      setClubIds([]);
    }
  }, [clubIdsParam]);

  useEffect(() => {
    if (clubIds.length === 0) {
      setMatches([]);
      setError("Nessun club preferito salvato.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError("");

    async function load() {
      try {
        const latestMatches = await Promise.all(
          clubIds.map(async (id) => {
            const response = await fetch("/api/club/" + id + "/matches", {
              cache: "no-store",
            });

            if (response.status < 200 || response.status >= 300) {
              throw new Error("Impossibile caricare il Club ID " + id + ".");
            }

            const result = await response.json();
            const list: Match[] = Array.isArray(result.matches)
              ? result.matches
              : [];

            const played = list
              .filter((match) => match.played === true)
              .sort(
                (a, b) =>
                  parseDate(b.datetime) - parseDate(a.datetime) ||
                  b.fixtureId - a.fixtureId,
              );

            if (played.length > 0) {
              return played[0];
            }

            const upcoming = list
              .filter((match) => match.played === false)
              .sort(
                (a, b) =>
                  parseDate(a.datetime) - parseDate(b.datetime) ||
                  a.fixtureId - b.fixtureId,
              );

            return upcoming.length > 0 ? upcoming[0] : null;
          }),
        );

        const validMatches = latestMatches.filter(
          (match): match is Match => match !== null,
        );

        const details = await Promise.all(
          validMatches.map(async (match) => {
            try {
              const response = await fetch(
                "/api/match/" + match.fixtureId,
                { cache: "no-store" },
              );

              if (response.status < 200 || response.status >= 300) {
                return {
                  ...match,
                  stadium: null,
                  events: [],
                  commentary: [],
                };
              }

              const detail = await response.json();

              return {
                ...match,
                stadium: detail.stadium || null,
                events: Array.isArray(detail.events) ? detail.events : [],
                commentary: Array.isArray(detail.commentary)
                  ? detail.commentary
                  : [],
              };
            } catch {
              return {
                ...match,
                stadium: null,
                events: [],
                commentary: [],
              };
            }
          }),
        );

        if (!cancelled) {
          setMatches(details);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Errore durante il caricamento.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [clubIds]);

  const entries = useMemo<ReplayEntry[]>(() => {
    return matches.map((match) => {
      const data = buildReplayData(match);
      const controller = new MatchReplayController(data, "M3", {
        home: match.home.name,
        away: match.away.name,
      });

      return {
        match,
        controller,
        kickoffMs: parseDate(match.datetime),
      };
    });
  }, [matches]);

  const totalDuration = useMemo(() => {
    if (entries.length === 0) return 0;
    return Math.max(...entries.map((entry) => entry.controller.durationSeconds));
  }, [entries]);

  useEffect(() => {
    const initial = entries.map((entry) => entry.controller.reset());
    setStates(initial);
    globalElapsedRef.current = 0;
    setGlobalElapsed(0);
    setPlaying(false);
    lastTimestampRef.current = null;
  }, [entries]);

  const applyGlobalElapsed = (nextGlobal: number) => {
    const bounded = Math.min(totalDuration, Math.max(0, nextGlobal));
    const nextStates = entries.map((entry) => {
      if (entry.match.played !== true) {
        return entry.controller.reset();
      }

      return entry.controller.setElapsedSeconds(
        Math.min(entry.controller.durationSeconds, bounded),
      );
    });

    globalElapsedRef.current = bounded;
    setGlobalElapsed(bounded);
    setStates(nextStates);

    console.log(
      "MULTIPLEX STATES",
     nextStates.map((state, index) => ({
       index,
       fixtureId: entries[index]?.match.fixtureId,
       minute: state.match_minute,
       score: state.home_score + "-" + state.away_score,
       scenes: state.visible_scenes.length,
     })),
   );
    if (bounded >= totalDuration && totalDuration > 0) {
      setPlaying(false);
    }
  };

  useEffect(() => {
    if (!playing) {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      lastTimestampRef.current = null;
      return;
    }

    const tick = (timestamp: number) => {
      if (lastTimestampRef.current === null) {
        lastTimestampRef.current = timestamp;
      }

      const delta = Math.max(
        0,
        (timestamp - lastTimestampRef.current) / 1000,
      );

      lastTimestampRef.current = timestamp;
      applyGlobalElapsed(globalElapsedRef.current + delta);

      if (globalElapsedRef.current < totalDuration) {
        animationRef.current = requestAnimationFrame(tick);
      } else {
        animationRef.current = null;
      }
    };

    animationRef.current = requestAnimationFrame(tick);

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      lastTimestampRef.current = null;
    };
  }, [playing, totalDuration, entries]);

  const togglePlay = () => {
    if (entries.length === 0) return;

    if (globalElapsedRef.current >= totalDuration) {
      applyGlobalElapsed(0);
    }

    setPlaying((value) => !value);
  };

  const reset = () => {
    applyGlobalElapsed(0);
    setPlaying(false);
  };

  const title =
    matches.length +
    " MATCH" +
    (matches.length === 1 ? "" : "ES");



  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <span>SV LIVE SCORE</span>
          <h1>Multiplex</h1>
        </div>
        <div className={styles.badge}>● SYNCED REPLAY</div>
      </header>

      <section className={styles.toolbar}>
        <div>
          <span>MATCH CENTER</span>
          <h2>{loading ? "Caricamento…" : title}</h2>
        </div>

        <button
          type="button"
          onClick={() => {
            window.location.href = "/";
          }}
        >
          ← HOME
        </button>
      </section>

      {error && <div className={styles.empty}>{error}</div>}
      {loading && <div className={styles.empty}>Caricamento partite…</div>}

      {!loading && !error && matches.length > 0 && (
        <>
          <section className={styles.controlPanel}>


            <div className={styles.controlActions}>
              <button
                type="button"
                className={styles.playButton}
                onClick={togglePlay}
              >
                {playing ? "❚❚ PAUSA" : "▶ PLAY ALL"}
              </button>
              <button
                type="button"
                className={styles.resetButton}
                onClick={reset}
              >
                ↺ RESET
              </button>
            </div>


          </section>

          <section className={styles.grid}>
            {entries.map((entry, index) => (
              <MatchCard
                key={
                  String(entry.match.fixtureId) +
                  "-" +
                  String(entry.match.homeClubId) +
                  "-" +
                  String(entry.match.awayClubId) +
                  "-" +
                  String(index)
                }
                entry={entry}
                state={states[index] || entry.controller.state()}
                globalElapsed={globalElapsed}
              />
            ))}
          </section>
        </>
      )}

      {!loading && !error && matches.length === 0 && (
        <div className={styles.empty}>Nessuna partita disponibile.</div>
      )}
    </main>
  );
}

export default function MultiplexPage() {
  return (
    <Suspense
      fallback={
        <main className={styles.page}>
          <div className={styles.empty}>Caricamento Multiplex…</div>
        </main>
      }
    >
      <MultiplexContent />
    </Suspense>
  );
}
