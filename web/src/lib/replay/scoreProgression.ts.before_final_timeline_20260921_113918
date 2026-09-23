import type { ScoreSnapshot } from "./types";

export interface ScoreProgressionFixture {
  home_club: number;
  away_club: number;
}

export interface ScoreProgressionEvent {
  event_type?: string;
  time?: number;
  club_id?: number | null;
  player_id?: number | null;
  event_player_id?: number | null;
  match_event_id?: number | null;
}

export class ScoreProgressionEngine {
  private readonly fixture: ScoreProgressionFixture;
  private readonly events: ScoreProgressionEvent[];

  private readonly homeClubId: number;
  private readonly awayClubId: number;

  constructor(
    fixture: ScoreProgressionFixture,
    events: ScoreProgressionEvent[],
  ) {
    this.fixture = fixture;
    this.events = [...events];

    this.homeClubId = Number(fixture.home_club);
    this.awayClubId = Number(fixture.away_club);
  }

  snapshots(): ScoreSnapshot[] {
    let homeScore = 0;
    let awayScore = 0;

    const result: ScoreSnapshot[] = [];

    const timeline = this.events
      .filter((event) => {
        const type = String(event.event_type ?? "").toUpperCase();
        return type === "GOAL" || type === "GOALCANCELLED";
      })
      .sort(
        (a, b) =>
          Number(a.time ?? 0) - Number(b.time ?? 0) ||
          Number(a.match_event_id ?? 0) - Number(b.match_event_id ?? 0),
      );

    const activeGoals = new Set<string>();

    for (const event of timeline) {
      const type = String(event.event_type ?? "").toUpperCase();
      const clubId = Number(event.club_id);
      const playerId = event.player_id ?? event.event_player_id;

      const key = [
        Number(event.time ?? 0),
        clubId,
        playerId == null ? "" : Number(playerId),
      ].join("|");

      if (type === "GOAL") {
        if (clubId === this.homeClubId) {
          homeScore += 1;
        } else if (clubId === this.awayClubId) {
          awayScore += 1;
        } else {
          throw new Error(
            `Goal belongs to unknown club ${clubId}`,
          );
        }

        activeGoals.add(key);
      } else if (type === "GOALCANCELLED") {
        if (!activeGoals.has(key)) {
          continue;
        }

        if (clubId === this.homeClubId) {
          homeScore = Math.max(0, homeScore - 1);
        } else if (clubId === this.awayClubId) {
          awayScore = Math.max(0, awayScore - 1);
        }

        activeGoals.delete(key);
      }

      result.push({
        match_minute: Number(event.time ?? 0),
        home_score: homeScore,
        away_score: awayScore,
      });
    }

    return result;
  }

  scoreAt(matchMinute: number): ScoreSnapshot {
    if (matchMinute < 0) {
      throw new Error(
        "Match minute cannot be negative",
      );
    }

    let homeScore = 0;
    let awayScore = 0;

    for (const snapshot of this.snapshots()) {
      if (snapshot.match_minute > matchMinute) {
        break;
      }

      homeScore = snapshot.home_score;
      awayScore = snapshot.away_score;
    }

    return {
      match_minute: matchMinute,
      home_score: homeScore,
      away_score: awayScore,
    };
  }
}