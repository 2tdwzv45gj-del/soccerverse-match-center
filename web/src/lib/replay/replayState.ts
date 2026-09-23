import type {
  ReplayMode,
  ReplayScheduleItem,
  ReplayState,
} from "./types";

import {
  REPLAY_MODE_SECONDS,
} from "./replaySchedule";

import {
  ScoreProgressionEngine,
  type ScoreProgressionEvent,
  type ScoreProgressionFixture,
} from "./scoreProgression";

export class ReplayStateEngine {
  private readonly schedule: ReplayScheduleItem[];
  private readonly replayMode: ReplayMode;
  private readonly scoreEngine: ScoreProgressionEngine;
  private readonly matchDurationMinutes: number;

  constructor(
    fixture: ScoreProgressionFixture,
    events: ScoreProgressionEvent[],
    schedule: ReplayScheduleItem[],
    replayMode: ReplayMode,
  ) {
    this.schedule = [...schedule];
    this.replayMode = replayMode;

    this.scoreEngine = new ScoreProgressionEngine(
      fixture,
      events,
    );

    const sceneMinutes = this.schedule
      .map((item) => item.scene.match_minute)
      .filter((minute) => minute >= 0);

    this.matchDurationMinutes = Math.max(
      90,
      ...(sceneMinutes.length > 0
        ? sceneMinutes
        : [90]),
    );
  }

  stateAt(elapsedSeconds: number): ReplayState {
    if (elapsedSeconds < 0) {
      throw new Error(
        "Replay time cannot be negative",
      );
    }

    const totalSeconds =
      REPLAY_MODE_SECONDS[this.replayMode];

    const elapsed = Math.min(
      Number(elapsedSeconds),
      totalSeconds,
    );

    const visible: ReplayScheduleItem[] = [];

    for (const item of this.schedule) {
      if (item.replay_seconds <= elapsed) {
        visible.push(item);
      } else {
        break;
      }
    }

    const currentScene =
      visible.length > 0
        ? visible[visible.length - 1]
        : null;

    const progress =
      totalSeconds > 0
        ? elapsed / totalSeconds
        : 0;

    const matchMinute = Math.min(
      this.matchDurationMinutes,
      Math.floor(
        progress *
          this.matchDurationMinutes,
      ),
    );

    const score = this.scoreEngine.scoreAt(
      matchMinute,
    );

    return {
      replay_mode: this.replayMode,
      elapsed_seconds: elapsed,
      match_minute: matchMinute,
      current_scene: currentScene,
      visible_scenes: visible,
      home_score: score.home_score,
      away_score: score.away_score,
    };
  }
}