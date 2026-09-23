import type {
  ReplayMode,
  ReplayScene,
  ReplayScheduleItem,
} from "./types";

export const REPLAY_MODE_SECONDS: Record<
  ReplayMode,
  number
> = {
  M2: 120,
  M3: 180,
  M5: 300,
  M10: 600,
};

export function buildReplaySchedule(
  scenes: ReplayScene[],
  mode: ReplayMode,
): ReplayScheduleItem[] {
  if (scenes.length === 0) {
    return [];
  }

  const ordered = [...scenes].sort(
    (a, b) =>
      a.match_minute - b.match_minute ||
      a.action_id - b.action_id,
  );

  const total = REPLAY_MODE_SECONDS[mode];

  // Regulation time is 90 minutes.
  // If official data contains stoppage-time events,
  // extend the replay clock accordingly.
  const matchDurationMinutes = Math.max(
    90,
    ...ordered
      .filter((scene) => scene.match_minute >= 0)
      .map((scene) => scene.match_minute),
  );

  return ordered.map((scene) => {
    const minute = Math.max(
      0,
      scene.match_minute,
    );

    const replaySeconds =
      (total * minute) /
      matchDurationMinutes;

    return {
      scene,
      replay_seconds: Math.min(
        total,
        replaySeconds,
      ),
    };
  });
}