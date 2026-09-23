import type {
  CommentarySubEvent,
  ReplayMode,
  ReplayScene,
  ReplayState,
} from "./types";

import {
  groupCommentaryActions,
} from "./commentaryActions";

import {
  composeActions,
} from "./commentaryComposer";

import {
  buildReplaySchedule,
  REPLAY_MODE_SECONDS,
} from "./replaySchedule";

import {
  ReplayStateEngine,
} from "./replayState";

export interface MatchReplayFixture {
  home_club: number;
  away_club: number;
  home_club_name?: string;
  away_club_name?: string;
}

export interface MatchReplayData {
  fixture: MatchReplayFixture;
  events: Array<{
    event_type?: string;
    time?: number;
    club_id?: number | null;
    player_id?: number | null;
    event_player_id?: number | null;
    match_event_id?: number | null;
  }>;
  commentary: CommentarySubEvent[];
}

export interface ReplayClubNames {
  home: string;
  away: string;
}

export interface ReplayPlayerResolver {
  getPlayerName(playerId: number): string | null;
}

export interface ReplayViewState extends ReplayState {
  current_kind: string | null;
  current_action_id: number | null;
}

export class MatchReplayController {
  private readonly matchData: MatchReplayData;
  private readonly mode: ReplayMode;
  private readonly clubNames: ReplayClubNames;
  private readonly playerResolver?: ReplayPlayerResolver;

  private readonly schedule: ReturnType<
    typeof buildReplaySchedule
  >;

  private readonly engine: ReplayStateEngine;

  private elapsedSeconds = 0;

  constructor(
    matchData: MatchReplayData,
    mode: ReplayMode = "M3",
    clubNames?: ReplayClubNames,
    playerResolver?: ReplayPlayerResolver,
  ) {
    this.matchData = matchData;
    this.mode = mode;
    this.playerResolver = playerResolver;

    const homeClubId = Number(
      matchData.fixture.home_club,
    );

    const awayClubId = Number(
      matchData.fixture.away_club,
    );

    this.clubNames = {
      home:
        clubNames?.home ??
        matchData.fixture.home_club_name ??
        String(homeClubId),

      away:
        clubNames?.away ??
        matchData.fixture.away_club_name ??
        String(awayClubId),
    };

    const subEvents = matchData.commentary.map(
      (item) => ({
        ...item,
        comm_sub_event_id:
          Number(item.comm_sub_event_id),
        comm_event_id:
          Number(item.comm_event_id),
        time: Number(item.time),
      }),
    );

    const actions =
      groupCommentaryActions(subEvents);

    const narratives =
      composeActions(actions);

    const scenes: ReplayScene[] =
      narratives.map((narrative) => {
        let clubName =
          narrative.club_name;

        /*
         * Same special handling used by the
         * desktop controller for saved chances.
         */
        if (
          narrative.kind === "chance_saved" &&
          narrative.club_name ===
            this.clubNames.home
        ) {
          clubName = this.clubNames.away;
        } else if (
          narrative.kind === "chance_saved" &&
          narrative.club_name ===
            this.clubNames.away
        ) {
          clubName = this.clubNames.home;
        } else if (
          narrative.club_name ===
          this.clubNames.home
        ) {
          clubName = this.clubNames.home;
        } else if (
          narrative.club_name ===
          this.clubNames.away
        ) {
          clubName = this.clubNames.away;
        }

        let playerName: string | null = null;

        if (
          narrative.kind === "chance_saved" &&
          narrative.goalkeeper_id &&
          this.playerResolver
        ) {
          playerName =
            this.playerResolver.getPlayerName(
              narrative.goalkeeper_id,
            );
        } else if (
          narrative.kind === "chance_saved" &&
          narrative.goalkeeper
        ) {
          playerName =
            narrative.goalkeeper;
        } else if (
          narrative.shooter_player_id &&
          this.playerResolver
        ) {
          playerName =
            this.playerResolver.getPlayerName(
              narrative.shooter_player_id,
            );
        }

        if (!playerName) {
          playerName =
            narrative.shooter_player ??
            narrative.substitute_on ??
            narrative.defender_player ??
            narrative.creator_player ??
            null;
        }

        return {
          action_id: narrative.action_id,
          match_minute: narrative.minute,
          kind: narrative.kind,
          club_name: clubName,
          player_name: playerName,
        };
      });

    this.schedule =
      buildReplaySchedule(
        scenes,
        mode,
      );

    this.engine =
      new ReplayStateEngine(
        matchData.fixture,
        matchData.events,
        this.schedule,
        mode,
      );
  }

  get durationSeconds(): number {
    return REPLAY_MODE_SECONDS[this.mode];
  }

  reset(): ReplayViewState {
    this.elapsedSeconds = 0;

    return this.state();
  }

  advance(seconds: number): ReplayViewState {
    this.elapsedSeconds = Math.min(
      this.durationSeconds,
      Math.max(
        0,
        this.elapsedSeconds + seconds,
      ),
    );

    return this.state();
  }

  state(): ReplayViewState {
    const state =
      this.engine.stateAt(
        this.elapsedSeconds,
      );

    const currentActionId =
      state.current_scene
        ? state.current_scene.scene.action_id
        : null;

    const currentKind =
      state.current_scene
        ? state.current_scene.scene.kind
        : null;

    return {
      ...state,
      current_action_id:
        currentActionId,
      current_kind:
        currentKind,
    };
  }

  setElapsedSeconds(
    seconds: number,
  ): ReplayViewState {
    this.elapsedSeconds = Math.min(
      this.durationSeconds,
      Math.max(0, seconds),
    );

    return this.state();
  }

  getElapsedSeconds(): number {
    return this.elapsedSeconds;
  }

  getSchedule() {
    return this.schedule;
  }
}