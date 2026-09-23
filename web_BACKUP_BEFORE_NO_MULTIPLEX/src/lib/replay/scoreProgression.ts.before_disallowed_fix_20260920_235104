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

    // Soccerverse can emit a GOAL immediately followed by
    // GOALCANCELLED for the same player, club and minute.
    // The cancelled goal must not alter the official score.
    const cancelledGoals = new Set<string>();

    for (const event of this.events) {
      if (
        String(event.event_type ?? "").toUpperCase() !==
        "GOALCANCELLED"
      ) {
        continue;
      }

      if (
        event.club_id === null ||
        event.club_id === undefined
      ) {
        continue;
      }

      const playerId =
        event.player_id ?? event.event_player_id;

      if (
        playerId === null ||
        playerId === undefined
      ) {
        continue;
      }

      const key = [
        Number(event.time ?? 0),
        Number(event.club_id),
        Number(playerId),
      ].join("|");

      cancelledGoals.add(key);
    }

    const goalEvents = this.events
      .filter((event) => {
        if (
          String(event.event_type ?? "").toUpperCase() !==
          "GOAL"
        ) {
          return false;
        }

        if (
          event.club_id === null ||
          event.club_id === undefined
        ) {
          return false;
        }

        const playerId =
          event.player_id ?? event.event_player_id;

        if (
          playerId === null ||
          playerId === undefined
        ) {
          return false;
        }

        const key = [
          Number(event.time ?? 0),
          Number(event.club_id),
          Number(playerId),
        ].join("|");

        return !cancelledGoals.has(key);
      })
      .sort(
        (a, b) =>
          Number(a.time ?? 0) -
            Number(b.time ?? 0) ||
          Number(a.match_event_id ?? 0) -
            Number(b.match_event_id ?? 0),
      );

    for (const event of goalEvents) {
      const clubId = Number(event.club_id);

      if (clubId === this.homeClubId) {
        homeScore += 1;
      } else if (clubId === this.awayClubId) {
        awayScore += 1;
      } else {
        throw new Error(
          `Goal belongs to unknown club ${clubId}`,
        );
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