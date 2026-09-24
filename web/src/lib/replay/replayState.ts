import type {
  ReplayMode,
  ReplayScheduleItem,
  ReplayState,
  ReplayTacticsState,
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
  private readonly tactics: ReplayTacticsState;

  constructor(
    fixture: ScoreProgressionFixture,
    events: ScoreProgressionEvent[],
    schedule: ReplayScheduleItem[],
    replayMode: ReplayMode,
    tactics: ReplayTacticsState,
  ) {
    this.schedule = [...schedule];
    this.replayMode = replayMode;
    this.tactics = tactics;

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

  private tacticsAt(
    matchMinute: number,
  ): ReplayTacticsState {
    const resolveSide = (
      side: ReplayTacticsState["home"],
    ): ReplayTacticsState["home"] => {
      const timeline = side.timeline;

      let formation = side.formation;
      let formationId = side.formation_id;
      let playStyle = side.play_style;
      let changed = false;
      let changeMinute: number | null = null;

      for (const item of timeline) {
        const minute = Number(item.time ?? -1);

        if (!Number.isFinite(minute) || minute > matchMinute) {
          continue;
        }

        const nextFormation =
          typeof item.formation_name === "string"
            ? item.formation_name
            : formation;

        const nextFormationId =
          Number.isFinite(Number(item.formation_id))
            ? Number(item.formation_id)
            : formationId;

        const nextPlayStyle =
          typeof item.play_style === "string"
            ? item.play_style
            : playStyle;

        const formationChanged =
          nextFormation !== formation;

        const styleChanged =
          nextPlayStyle !== playStyle;

        if (formationChanged || styleChanged) {
          changed = true;
          changeMinute = minute;
        }

        formation = nextFormation;
        formationId = nextFormationId;
        playStyle = nextPlayStyle;
      }

      return {
        formation,
        formation_id: formationId,
        play_style: playStyle,
        changed,
        change_minute: changeMinute,
        timeline,
      };
    };

    return {
      home: resolveSide(this.tactics.home),
      away: resolveSide(this.tactics.away),
    };
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
      tactics: this.tacticsAt(matchMinute),
    };
  }
}