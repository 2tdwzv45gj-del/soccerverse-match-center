"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  MatchReplayController,
  type MatchReplayData,
} from "./matchReplayController";

import type {
  ReplayViewState,
} from "./matchReplayController";

type ReplayPlayerProps = {
  data: MatchReplayData;
  homeName: string;
  awayName: string;
  onStateChange?: (
    state: ReplayViewState,
  ) => void;
};

function sceneIcon(kind: string) {
  if (kind === "goal") return "⚽";
  if (kind === "chance_saved") return "🧤";
  if (kind === "chance_offtarget") return "🎯";
  if (kind === "chance_tackled") return "🛡️";
  if (kind === "substitution") return "🔄";
  if (kind === "shot") return "🎯";

  return "•";
}

function sceneLabel(kind: string) {
  if (kind === "goal") return "GOAL";
  if (kind === "chance_saved") return "SAVE";
  if (kind === "chance_offtarget") return "OFF TARGET";
  if (kind === "chance_tackled") return "TACKLE";
  if (kind === "substitution") return "SUBSTITUTION";
  if (kind === "shot") return "SHOT";

  return "ACTION";
}

export default function ReplayPlayer({
  data,
  homeName,
  awayName,
  onStateChange,
}: ReplayPlayerProps) {
  const controller = useMemo(
    () =>
      new MatchReplayController(
        data,
        "M3",
      ),
    [],
  );

  const onStateChangeRef = useRef(onStateChange);

  useEffect(() => {
    onStateChangeRef.current = onStateChange;
  }, [onStateChange]);

  const [state, setState] =
    useState<ReplayViewState>(
      () => controller.reset(),
    );

  const [playing, setPlaying] =
    useState(false);

  const animationRef =
    useRef<number | null>(null);

  const audioRef = useRef<Record<string, HTMLAudioElement>>({});
  const playedAudioEventsRef = useRef<Set<string>>(new Set());
  const previousMinuteRef = useRef(0);

  const playAudio = (key: string, src: string) => {
    if (playedAudioEventsRef.current.has(key)) return;

    const audio =
      audioRef.current[key] ?? new Audio(src);

    audioRef.current[key] = audio;
    audio.currentTime = 0;
    playedAudioEventsRef.current.add(key);
    void audio.play().catch(() => {});
  };

  const lastTimestampRef =
    useRef<number | null>(null);

  useEffect(() => {
    const initial =
      controller.reset();

    setState(initial);
    setPlaying(false);

    onStateChangeRef.current?.(initial);
  }, [controller]);

  useEffect(() => {
    if (!playing) {
      if (
        animationRef.current !== null
      ) {
        cancelAnimationFrame(
          animationRef.current,
        );
        animationRef.current = null;
      }

      lastTimestampRef.current = null;

      return;
    }

    const tick = (
      timestamp: number,
    ) => {
      if (
        lastTimestampRef.current === null
      ) {
        lastTimestampRef.current =
          timestamp;
      }

      const delta =
        (timestamp -
          lastTimestampRef.current) /
        1000;

      lastTimestampRef.current =
        timestamp;

      const previousMinute = previousMinuteRef.current;
      const next =
        controller.advance(delta);

      const nextMinute = next.match_minute;

      if (nextMinute > previousMinute) {
        for (const event of data.events) {
          const minute = Number(event.time ?? 0);
          const type = String(event.event_type ?? "").toUpperCase();
          const eventId = Number(
            event.match_event_id ??
              event.event_player_id ??
              event.player_id ??
              minute,
          );

          if (
            minute > previousMinute &&
            minute <= nextMinute
          ) {
            if (type === "GOAL") {
              playAudio("goal-" + eventId, "/audio/goal.wav");
            } else if (
              type === "REDCARD" ||
              type === "SECONDYELLOWCARD"
            ) {
              playAudio(
                "red-" + eventId,
                "/audio/red_card.wav",
              );
            }
          }
        }

        for (const scene of next.visible_scenes) {
          if (
            scene.scene.kind === "substitution" &&
            scene.scene.match_minute > previousMinute &&
            scene.scene.match_minute <= nextMinute
          ) {
            playAudio(
              "sub-" + scene.scene.action_id,
              "/audio/substitution.wav",
            );
          }
        }
      }

      previousMinuteRef.current = nextMinute;

      setState(next);
      onStateChangeRef.current?.(next);

      if (
        next.elapsed_seconds >=
        controller.durationSeconds
      ) {
        playAudio(
          "match-end",
          "/audio/match_end.wav",
        );
        setPlaying(false);
        animationRef.current = null;
        lastTimestampRef.current = null;
        return;
      }

      animationRef.current =
        requestAnimationFrame(tick);
    };

    animationRef.current =
      requestAnimationFrame(tick);

    return () => {
      if (
        animationRef.current !== null
      ) {
        cancelAnimationFrame(
          animationRef.current,
        );

        animationRef.current = null;
      }

      lastTimestampRef.current = null;
    };
  }, [
    playing,
    controller,
  ]);

  function togglePlay() {
    if (
      state.elapsed_seconds >=
      controller.durationSeconds
    ) {
      const reset =
        controller.reset();

      playedAudioEventsRef.current.clear();
      previousMinuteRef.current = 0;

      setState(reset);
      onStateChangeRef.current?.(reset);
    }

    if (!playing) {
      playAudio("match-start", "/audio/match_start.wav");
    }

    setPlaying((value) => !value);
  }

  function resetReplay() {
    const reset =
      controller.reset();

    playedAudioEventsRef.current.clear();
    previousMinuteRef.current = 0;

    setState(reset);
    onStateChangeRef.current?.(reset);
    setPlaying(false);
  }

  function seek(value: number) {
    const next =
      controller.setElapsedSeconds(
        value,
      );

    previousMinuteRef.current =
      next.match_minute;

    setState(next);
    onStateChangeRef.current?.(next);
  }

  const progress =
    controller.durationSeconds > 0
      ? (
          state.elapsed_seconds /
          controller.durationSeconds
        ) *
        100
      : 0;

  return (
    <section
      style={{
        marginTop: 24,
        marginBottom: 28,
        padding: 22,
        borderRadius: 20,
        border:
          "1px solid rgba(255,255,255,0.09)",
        background:
          "linear-gradient(145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.025))",
        boxShadow:
          "0 18px 50px rgba(0,0,0,0.24)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          gap: 16,
          marginBottom: 18,
        }}
      >
        <div>
          <span
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: 1.5,
              opacity: 0.55,
            }}
          >
            SV LIVE SCORE
          </span>

          <h2
            style={{
              margin:
                "5px 0 0",
              fontSize: 22,
            }}
          >
            Match Replay
          </h2>
        </div>

        <div
          style={{
            textAlign: "right",
          }}
        >
          <div
            style={{
              fontSize: 12,
              opacity: 0.55,
            }}
          >
            SOCCERVERSE
          </div>

          <strong
            style={{
              fontSize: 25,
            }}
          >
            {state.match_minute}&apos;
          </strong>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "1fr auto 1fr",
          alignItems: "center",
          gap: 16,
          padding:
            "16px 12px 20px",
        }}
      >
        <div
          style={{
            textAlign: "right",
            fontWeight: 800,
            fontSize: 18,
          }}
        >
          {homeName}
        </div>

        <div
          style={{
            fontSize: 32,
            fontWeight: 900,
            letterSpacing: 2,
            whiteSpace: "nowrap",
          }}
        >
          {state.home_score}
          <span
            style={{
              opacity: 0.3,
              margin:
                "0 7px",
            }}
          >
            -
          </span>
          {state.away_score}
        </div>

        <div
          style={{
            fontWeight: 800,
            fontSize: 18,
          }}
        >
          {awayName}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 7,
          fontSize: 11,
          fontWeight: 700,
          opacity: 0.58,
        }}
      >
        <span>1&apos;</span>
        <span>15&apos;</span>
        <span>30&apos;</span>
        <span>45&apos;</span>
        <span>60&apos;</span>
        <span>75&apos;</span>
        <span>90+</span>
      </div>

      <div
        style={{
          position: "relative",
          width: "100%",
        }}
      >
        <input
          type="range"
          min={0}
          max={controller.durationSeconds}
          step={0.1}
          value={state.elapsed_seconds}
          onChange={(event) =>
            seek(Number(event.target.value))
          }
          style={{
            width: "100%",
            cursor: "pointer",
            accentColor: "#55c2ff",
          }}
        />

        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: "50%",
            transform: "translateY(-50%)",
            height: 24,
            pointerEvents: "none",
          }}
        >
          {(() => {
            const markerEvents = data.events
              .filter((event) => Number(event.time ?? 0) <= state.match_minute)
              .filter((event) => {
                const type = String(event.event_type ?? "").toUpperCase();
                return [
                  "GOAL",
                  "GOALCANCELLED",
                  "YELLOWCARD",
                  "SECONDYELLOWCARD",
                  "REDCARD",
                ].includes(type);
              });

            const goalKey = (event: any) => [
              Number(event.time ?? 0),
              Number(event.club_id),
              event.player_id ?? event.event_player_id ?? "",
            ].join("|");

            const cancelledGoals = new Set(
              data.events
                .filter(
                  (event) =>
                    String(event.event_type ?? "").toUpperCase() ===
                    "GOALCANCELLED",
                )
                .map(goalKey),
            );

            const markers = markerEvents
              .filter((event) => {
                const type = String(event.event_type ?? "").toUpperCase();
                if (type !== "GOAL") return true;
                return !cancelledGoals.has(goalKey(event));
              })
              .map((event) => ({
                type: String(event.event_type ?? "").toUpperCase(),
                minute: Number(event.time ?? 0),
              }));

            const cancelledMarkers = data.events
              .filter(
                (event) =>
                  String(event.event_type ?? "").toUpperCase() ===
                    "GOALCANCELLED" &&
                  Number(event.time ?? 0) <= state.match_minute,
              )
              .map((event) => ({
                type: "GOALCANCELLED",
                minute: Number(event.time ?? 0),
              }));

            const allMarkers = [...markers, ...cancelledMarkers];

            return allMarkers.map((marker, index) => {
              const minute = marker.minute;
              const position =
                controller.durationSeconds > 0
                  ? Math.min(
                      100,
                      Math.max(
                        0,
                        (minute / 90) * 100,
                      ),
                    )
                  : 0;

              let icon = "🟨";

              if (marker.type === "GOAL") icon = "⚽";
              if (marker.type === "GOALCANCELLED") icon = "🚫";
              if (marker.type === "REDCARD") icon = "🟥";
              if (marker.type === "SECONDYELLOWCARD") icon = "🟨🟥";

              return (
                <span
                  key={
                    marker.type + "-" +
                    String(minute) + "-" +
                    String(index)
                  }
                  title={
                    marker.type === "GOAL"
                      ? "Gol"
                      : marker.type === "GOALCANCELLED"
                        ? "Gol annullato"
                        : marker.type === "REDCARD"
                          ? "Espulsione"
                          : marker.type === "SECONDYELLOWCARD"
                            ? "Secondo giallo"
                            : "Ammonizione"
                  }
                  style={{
                    position: "absolute",
                    left: `${position}%`,
                    top: 0,
                    transform: "translateX(-50%)",
                    fontSize: 15,
                    lineHeight: "24px",
                    filter: "drop-shadow(0 1px 2px rgba(0,0,0,.8))",
                  }}
                >
                  {icon}
                </span>
              );
            });
          })()}

          {state.visible_scenes
            .filter(
              (item) =>
                item.scene.kind === "substitution" &&
                item.scene.match_minute <= state.match_minute,
            )
            .map((item, index) => {
              const minute = item.scene.match_minute;
              const position =
                controller.durationSeconds > 0
                  ? Math.min(
                      100,
                      Math.max(
                        0,
                        (minute / 90) * 100,
                      ),
                    )
                  : 0;

              return (
                <span
                  key={"sub-" + String(item.scene.action_id) + "-" + String(index)}
                  title="Sostituzione"
                  style={{
                    position: "absolute",
                    left: `${position}%`,
                    top: 0,
                    transform: "translateX(-50%)",
                    fontSize: 15,
                    lineHeight: "24px",
                    filter: "drop-shadow(0 1px 2px rgba(0,0,0,.8))",
                  }}
                >
                  🔄
                </span>
              );
            })}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent:
            "center",
          gap: 10,
          marginTop: 18,
        }}
      >
        <button
          type="button"
          onClick={togglePlay}
          style={{
            border: 0,
            borderRadius: 12,
            padding:
              "11px 22px",
            fontWeight: 800,
            fontSize: 14,
            cursor: "pointer",
            background:
              "#55c2ff",
            color: "#071018",
          }}
        >
          {playing
            ? "⏸ PAUSA"
            : "▶ AVVIA REPLAY"}
        </button>

        <button
          type="button"
          onClick={resetReplay}
          style={{
            border:
              "1px solid rgba(255,255,255,0.12)",
            borderRadius: 12,
            padding:
              "11px 18px",
            fontWeight: 700,
            fontSize: 14,
            cursor: "pointer",
            background:
              "rgba(255,255,255,0.05)",
            color: "inherit",
          }}
        >
          ↺ RESET
        </button>
      </div>
    </section>
  );
}