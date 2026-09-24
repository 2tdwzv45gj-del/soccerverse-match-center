"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReplayPlayer from "@/lib/replay/ReplayPlayer";
import LiveCommentary from "@/lib/commentary/LiveCommentary";
import { buildLiveCommentary, getCurrentCommentary } from "@/lib/commentary/commentaryComposer";

import type {
  ReplayMode,
  ReplayTacticsState,
} from "@/lib/replay/types";
type MatchData = {
  fixtureId: number;
  fixture: Record<string, any>;
  events: Record<string, any>[];
  commentary: Record<string, any>[];
  substitutions: Record<string, any>[];
  tactics?: { home?: Record<string, any> | null; away?: Record<string, any> | null };
  injuries: {
    minute: number;
    player_id: number;
    player_name: string;
    club_id: number;
    club_name: string;
    side: string;
  }[];
  startingPlayers: {
    player_id: number;
    player_name: string;
    side: string;
    club_id: number;
    start_ix: number;
  }[];
  stadium?: { id: number; name: string; image: string } | null;
};

type Club = {
  id: number;
  name: string;
  colors: number[] | null;
  logo: string | null;
};

function clubColor(club: Club | null) {
  if (club?.colors?.length === 3) {
    return "rgb(" + club.colors.join(", ") + ")";
  }

  return "#55c2ff";
}

function eventType(event: Record<string, any>) {
  return String(
    event.event_type || event.type || "EVENT"
  ).toUpperCase();
}

function eventIcon(type: string) {
  if (type === "GOAL") return "⚽";
  if (type === "GOALCANCELLED") return "🚫";
  if (type === "YELLOWCARD") return "🟨";
  if (type === "SECONDYELLOWCARD") return "🟨🟥";
  if (type === "REDCARD") return "🟥";
  if (type === "SUB") return "🔄";
  if (type === "SHOT") return "🎯";
  if (type === "SAVE") return "🧤";
  if (type === "FOUL") return "⚠️";

  return "•";
}

function eventLabel(type: string) {
  const labels: Record<string, string> = {
    GOAL: "GOAL",
    GOALCANCELLED: "GOAL CANCELLED",
    YELLOWCARD: "YELLOW CARD",
    SECONDYELLOWCARD: "SECOND YELLOW",
    REDCARD: "RED CARD",
    SUB: "SUBSTITUTION",
    SHOT: "SHOT",
    SAVE: "SAVE",
    CHANCE: "CHANCE",
    ASSISTEDCHANCE: "ASSISTED CHANCE",
    OFFTARGET: "OFF TARGET",
    FOUL: "FOUL",
    WARNED: "WARNING",
    TACKLE: "TACKLE",
  };

  return labels[type] || type.replaceAll("_", " ");
}

export default function MatchDetailPage() {
  const params = useParams<{ fixtureId: string }>();
  const router = useRouter();

  const [data, setData] = useState<MatchData | null>(null);
  const [home, setHome] = useState<Club | null>(null);
  const [away, setAway] = useState<Club | null>(null);
  const [loading, setLoading] = useState(true);
  const [replayScore, setReplayScore] = useState<string | null>(null);
  const [replayMinute, setReplayMinute] = useState<number>(0);
  const [replayTactics, setReplayTactics] =
    useState<ReplayTacticsState | null>(null);
  const [replayMode, setReplayMode] = useState<ReplayMode>("M5");
  const [showLineups, setShowLineups] = useState(false);
  const [liveCommentary, setLiveCommentary] = useState<ReturnType<typeof buildLiveCommentary>>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          "/api/match/" + params.fixtureId,
          { cache: "no-store" }
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(
            result?.error || "Impossibile caricare la partita."
          );
        }

        setData(result);
        setLiveCommentary(buildLiveCommentary(result.commentary || []));

        const fixture = result.fixture;

        const homeResponse = await fetch(
          "/api/club/" + Number(fixture.home_club),
          { cache: "no-store" }
        );

        const awayResponse = await fetch(
          "/api/club/" + Number(fixture.away_club),
          { cache: "no-store" }
        );

        if (homeResponse.ok) {
          setHome(await homeResponse.json());
        }

        if (awayResponse.ok) {
          setAway(await awayResponse.json());
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Errore durante il caricamento."
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [params.fixtureId]);

  if (loading) {
    return (
      <main className="matchPage">
        <div className="matchContainer">
          <button
            className="backButton"
            onClick={() => router.back()}
          >
            ← Match Center
          </button>

          <div className="matchLoading">
            Caricamento partita…
          </div>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="matchPage">
        <div className="matchContainer">
          <button
            className="backButton"
            onClick={() => router.back()}
          >
            ← Match Center
          </button>

          <div className="matchError">
            {error || "Partita non trovata."}
          </div>
        </div>
      </main>
    );
  }

  const fixture = data.fixture;

  const homeName =
    home?.name ||
    fixture.home_club_name ||
    "Club " + fixture.home_club;

  const awayName =
    away?.name ||
    fixture.away_club_name ||
    "Club " + fixture.away_club;

  const homeGoals = Number(
    fixture.home_goals ?? 0
  );

  const awayGoals = Number(
    fixture.away_goals ?? 0
  );

  const eventMinute = (event: any) => {
    const raw = event.time ?? event.time_minutes ?? event.time_display ?? 0;
    const match = String(raw).match(/\d+/);
    return match ? Number(match[0]) : 0;
  };

  const events = [...data.events].sort(
    (a, b) => eventMinute(a) - eventMinute(b)
  );

  const visibleEvents = events.filter((event) =>
    eventMinute(event) <= replayMinute
  );

  const visibleSubstitutions = data.substitutions.filter((sub) =>
    Number(sub.time ?? 0) <= replayMinute
  );

  const goalEventKey = (event: any) => [
    eventMinute(event),
    Number(event.club_id),
    event.player_id ?? event.event_player_id ?? "",
  ].join("|");

  const cancelledGoalKeys = new Set(
    events
      .filter((event) => eventType(event) === "GOALCANCELLED")
      .map(goalEventKey),
  );

  const validGoalEvents = visibleEvents.filter(
    (event) =>
      eventType(event) === "GOAL" &&
      !cancelledGoalKeys.has(goalEventKey(event)),
  );

  const finalHomeGoals = events.filter(
    (event) =>
      eventType(event) === "GOAL" &&
      Number(event.club_id) === Number(data.fixture.home_club) &&
      !cancelledGoalKeys.has(goalEventKey(event)),
  ).length;

  const finalAwayGoals = events.filter(
    (event) =>
      eventType(event) === "GOAL" &&
      Number(event.club_id) === Number(data.fixture.away_club) &&
      !cancelledGoalKeys.has(goalEventKey(event)),
  ).length;

  const timelineItems = [
    ...visibleEvents.map((event, index) => ({
      kind: "event" as const,
      time: eventMinute(event),
      event,
      sub: null,
      index,
    })),
    ...visibleSubstitutions.map((sub, index) => ({
      kind: "substitution" as const,
      time: Number(sub.time ?? 0),
      event: null,
      sub,
      index,
    })),
  ].sort((a, b) => a.time - b.time || a.index - b.index);

  const currentCommentary = getCurrentCommentary(liveCommentary, replayMinute);

  return (
    <main className="matchPage">
      <div className="matchContainer">

        <button
          className="backButton"
          onClick={() => router.back()}
        >
          ← Match Center
        </button>

        <section className="scoreHeader">

          <div className="competition">
            {fixture.comp_name ||
              fixture.league_name ||
              "SOCCERVERSE MATCH"}
          </div>

          <div className="fixtureMeta">
            FIXTURE #{data.fixtureId}
          </div>

          <div className="scoreTeams">

            <div className="scoreTeam scoreTeamHome">
              <div
                className="scoreLogo scoreLogoLarge"
                style={{
                  borderColor: clubColor(home),
                  boxShadow: `0 0 40px ${clubColor(home)}55`,
                }}
              >
                {home?.logo ? (
                  <img src={home.logo} alt={homeName} />
                ) : (
                  <span>⚽</span>
                )}
              </div>

              <h1>{homeName}</h1>
              <small>HOME</small>

              <div className="scoreTeamEvents">
                {validGoalEvents
                  .filter(
                    (event) =>
                      Number(event.club_id) === Number(data.fixture.home_club),
                  )
                  .map((event, index) => {
                    const e = event as any;
                    const minute = Number(event.time ?? event.time_minutes ?? 0);
                    return (
                      <div className="scoreEvent scoreEventGoal" key={`home-goal-${minute}-${index}`}>
                        <span className="scoreEventIcon">⚽</span>
                        <span>
                          <strong>{e.player_name || e.event_player_name || "Gol"}</strong>
                          <small>{minute}&apos;</small>
                        </span>
                      </div>
                    );
                  })}

                {visibleEvents
                  .filter(
                    (event) =>
                      Number(event.club_id) === Number(data.fixture.home_club) &&
                      ["REDCARD", "SECONDYELLOWCARD"].includes(
                        String(event.event_type ?? "").toUpperCase(),
                      ),
                  )
                  .map((event, index) => {
                    const e = event as any;
                    const minute = Number(event.time ?? event.time_minutes ?? 0);
                    return (
                      <div className="scoreEvent scoreEventRed" key={`home-red-${minute}-${index}`}>
                        <span className="scoreEventIcon">🟥</span>
                        <span>
                          <strong>{e.player_name || e.event_player_name || "Espulsione"}</strong>
                          <small>{minute}&apos;</small>
                        </span>
                      </div>
                    );
                  })}
              </div>
            </div>

            <div className="bigScore">
              <strong>{replayScore ?? `${finalHomeGoals} - ${finalAwayGoals}`}</strong>
              <span>{fixture.datetime || fixture.date || ""}</span>
              <em>REPLAY</em>
            </div>

            <div className="scoreTeam scoreTeamAway">
              <div
                className="scoreLogo scoreLogoLarge"
                style={{
                  borderColor: clubColor(away),
                  boxShadow: `0 0 40px ${clubColor(away)}55`,
                }}
              >
                {away?.logo ? (
                  <img src={away.logo} alt={awayName} />
                ) : (
                  <span>⚽</span>
                )}
              </div>

              <h1>{awayName}</h1>
              <small>AWAY</small>

              <div className="scoreTeamEvents">
                {validGoalEvents
                  .filter(
                    (event) =>
                      Number(event.club_id) === Number(data.fixture.away_club),
                  )
                  .map((event, index) => {
                    const e = event as any;
                    const minute = Number(event.time ?? event.time_minutes ?? 0);
                    return (
                      <div className="scoreEvent scoreEventGoal" key={`away-goal-${minute}-${index}`}>
                        <span className="scoreEventIcon">⚽</span>
                        <span>
                          <strong>{e.player_name || e.event_player_name || "Gol"}</strong>
                          <small>{minute}&apos;</small>
                        </span>
                      </div>
                    );
                  })}

                {visibleEvents
                  .filter(
                    (event) =>
                      Number(event.club_id) === Number(data.fixture.away_club) &&
                      ["REDCARD", "SECONDYELLOWCARD"].includes(
                        String(event.event_type ?? "").toUpperCase(),
                      ),
                  )
                  .map((event, index) => {
                    const e = event as any;
                    const minute = Number(event.time ?? event.time_minutes ?? 0);
                    return (
                      <div className="scoreEvent scoreEventRed" key={`away-red-${minute}-${index}`}>
                        <span className="scoreEventIcon">🟥</span>
                        <span>
                          <strong>{e.player_name || e.event_player_name || "Espulsione"}</strong>
                          <small>{minute}&apos;</small>
                        </span>
                      </div>
                    );
                  })}
              </div>
            </div>

          </div>
        </section>

        {replayTactics && (
          <section className="tacticsSection">
            <div className="tacticsHeader">
              <span>TACTICS & MENTALITY</span>
              <small>{replayMinute}&apos;</small>
            </div>

            <div className="tacticsGrid">
              <div className="tacticsTeam">
                <div className="tacticsTeamName">{homeName}</div>
                <div className="tacticsFormation">
                  {replayTactics.home.formation ?? "—"}
                </div>
                <div className="tacticsStyle">
                  {replayTactics.home.play_style ?? "—"}
                </div>
                {replayTactics.home.changed &&
                  replayTactics.home.change_minute !== null && (
                    <div className="tacticsChanged">
                      CHANGED @ {replayTactics.home.change_minute}&apos;
                    </div>
                  )}
                {replayTactics.home.timeline.length > 0 && (
                  <div className="tacticsTimeline">
                    {replayTactics.home.timeline
                      .filter(
                        (item) =>
                          item.time !== undefined &&
                          Number(item.time) <= replayMinute,
                      )
                      .map((item, index) => (
                        <span key={`home-tactic-${item.time}-${index}`}>
                          {item.time}&apos; {item.play_style ?? "—"}
                        </span>
                      ))}
                  </div>
                )}
              </div>

              <div className="tacticsVs">VS</div>

              <div className="tacticsTeam">
                <div className="tacticsTeamName">{awayName}</div>
                <div className="tacticsFormation">
                  {replayTactics.away.formation ?? "—"}
                </div>
                <div className="tacticsStyle">
                  {replayTactics.away.play_style ?? "—"}
                </div>
                {replayTactics.away.changed &&
                  replayTactics.away.change_minute !== null && (
                    <div className="tacticsChanged">
                      CHANGED @ {replayTactics.away.change_minute}&apos;
                    </div>
                  )}
                {replayTactics.away.timeline.length > 0 && (
                  <div className="tacticsTimeline">
                    {replayTactics.away.timeline
                      .filter(
                        (item) =>
                          item.time !== undefined &&
                          Number(item.time) <= replayMinute,
                      )
                      .map((item, index) => (
                        <span key={`away-tactic-${item.time}-${index}`}>
                          {item.time}&apos; {item.play_style ?? "—"}
                        </span>
                      ))}
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {data.stadium && (
          <section
            style={{
              position: "relative",
              overflow: "hidden",
              minHeight: "240px",
              marginTop: "24px",
              borderRadius: "24px",
              border: "1px solid rgba(255,255,255,0.08)",
              background: "#0d141e",
              boxShadow: "0 18px 50px rgba(0,0,0,0.28)",
            }}
          >
            <img
              src={data.stadium.image}
              alt={data.stadium.name}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />

            <div
              style={{
                position: "absolute",
                inset: 0,
                background:
                  "linear-gradient(90deg, rgba(5,9,14,0.96) 0%, rgba(5,9,14,0.72) 45%, rgba(5,9,14,0.25) 100%)",
              }}
            />

            <div
              style={{
                position: "relative",
                zIndex: 1,
                minHeight: "240px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                padding: "30px",
              }}
            >
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 800,
                  letterSpacing: "0.18em",
                  color: "rgba(255,255,255,0.55)",
                }}
              >
                MATCH VENUE
              </span>

              <h2
                style={{
                  margin: "7px 0 0",
                  fontSize: "30px",
                  lineHeight: 1.08,
                  fontWeight: 800,
                  color: "#fff",
                }}
              >
                🏟️ {data.stadium.name}
              </h2>

              <span
                style={{
                  marginTop: "8px",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.52)",
                }}
              >
                Soccerverse Stadium · ID {data.stadium.id}
              </span>
            </div>
          </section>
        )}

        <div style={{ display: "flex", justifyContent: "center", margin: "14px 0 8px" }}>
          <button
            type="button"
            onClick={() => setShowLineups(true)}
            style={{
              border: "1px solid rgba(85,194,255,.35)",
              borderRadius: 9,
              padding: "8px 14px",
              fontWeight: 800,
              fontSize: 12,
              cursor: "pointer",
              background: "rgba(85,194,255,.08)",
              color: "#55c2ff",
            }}
          >
            👥 FORMAZIONI INIZIALI
          </button>
        </div>

        {showLineups && (
          <div
            onClick={() => setShowLineups(false)}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 1000,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 16,
              background: "rgba(0,0,0,.78)",
            }}
          >
            <div
              onClick={(event) => event.stopPropagation()}
              style={{
                width: "min(760px, 100%)",
                maxHeight: "85vh",
                overflowY: "auto",
                border: "1px solid rgba(255,255,255,.12)",
                borderRadius: 18,
                background: "#111",
                boxShadow: "0 24px 80px rgba(0,0,0,.55)",
                padding: 20,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: ".14em", opacity: .6 }}>
                    STARTING LINEUPS
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 900, marginTop: 4 }}>
                    {homeName} <span style={{ opacity: .4 }}>VS</span> {awayName}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setShowLineups(false)}
                  aria-label="Chiudi"
                  style={{
                    border: "1px solid rgba(255,255,255,.12)",
                    borderRadius: 9,
                    width: 34,
                    height: 34,
                    cursor: "pointer",
                    background: "rgba(255,255,255,.05)",
                    color: "inherit",
                    fontSize: 18,
                  }}
                >
                  ✕
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
                {[
                  { side: "home", name: homeName },
                  { side: "away", name: awayName },
                ].map((team) => (
                  <div
                    key={team.side}
                    style={{
                      border: "1px solid rgba(255,255,255,.08)",
                      borderRadius: 14,
                      padding: 14,
                      background: "rgba(255,255,255,.025)",
                    }}
                  >
                    <div style={{ fontWeight: 900, fontSize: 15, marginBottom: 10 }}>
                      {team.name}
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {data.startingPlayers
                        .filter((player) => player.side === team.side)
                        .sort((a, b) => a.start_ix - b.start_ix)
                        .map((player) => (
                          <div
                            key={player.player_id}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 8,
                              padding: "7px 9px",
                              borderRadius: 8,
                              background: "rgba(255,255,255,.035)",
                              fontSize: 13,
                            }}
                          >
                            <span style={{ width: 20, opacity: .4, fontSize: 11 }}>
                              {player.start_ix + 1}
                            </span>
                            <span style={{ fontWeight: 700 }}>
                              {player.player_name}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            margin: "18px 0 10px",
            flexWrap: "wrap",
          }}
        >
          <span
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.12em",
              opacity: 0.65,
              marginRight: 4,
            }}
          >
            LIVE DURATION
          </span>
          {(["M2", "M3", "M5", "M10"] as ReplayMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setReplayMode(mode)}
              style={{
                border: replayMode === mode
                  ? "1px solid rgba(85,194,255,.9)"
                  : "1px solid rgba(255,255,255,.12)",
                borderRadius: 9,
                padding: "7px 12px",
                fontWeight: 800,
                fontSize: 12,
                cursor: "pointer",
                background: replayMode === mode
                  ? "rgba(85,194,255,.16)"
                  : "rgba(255,255,255,.05)",
                color: replayMode === mode
                  ? "#55c2ff"
                  : "inherit",
              }}
            >
              {mode.replace("M", "")} MIN
            </button>
          ))}
        </div>

        <ReplayPlayer
          mode={replayMode}
          data={{
            fixture: {
              home_club: Number(data.fixture.home_club),
              away_club: Number(data.fixture.away_club),
              home_club_name: homeName,
              away_club_name: awayName,
            },
            events: data.events.map((event) => ({
              event_type: event.event_type,
              time: Number(event.time ?? event.time_minutes ?? 0),
              club_id: event.club_id ?? null,
              player_id: event.player_id ?? null,
              event_player_id: event.event_player_id ?? null,
              match_event_id: event.match_event_id ?? null,
            })),
            commentary: data.commentary.map((event) => ({
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
            injuries: data.injuries ?? [],
            startingPlayers: data.startingPlayers ?? [],
            tactics: data.tactics ?? undefined,
          }}
          homeName={homeName}
          awayName={awayName}
          onStateChange={(state) => {
            setReplayScore(`${state.home_score}-${state.away_score}`);
            setReplayMinute(state.match_minute);
            setReplayTactics(state.tactics);
          }}
        />

        <LiveCommentary item={currentCommentary} />
      </div>
    </main>
  );
}