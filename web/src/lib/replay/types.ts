export type ReplayMode = "M2" | "M3" | "M5" | "M10";

export interface CommentarySubEvent {
  comm_sub_event_id: number;
  comm_event_id: number;
  time: number;
  category: string;

  player_one_id?: number | null;
  player_one_name?: string | null;

  player_two_id?: number | null;
  player_two_name?: string | null;

  club_one_id?: number | null;
  club_one_name?: string | null;
}

export interface CommentaryAction {
  comm_event_id: number;
  time: number;
  club_one_id: number | null;
  club_one_name: string | null;
  sub_events: CommentarySubEvent[];
}

export interface NarrativeIntent {
  action_id: number;
  minute: number;
  kind: string;

  creator_player: string | null;
  shooter_player: string | null;
  defender_player: string | null;
  goalkeeper: string | null;
  substitute_on: string | null;
  substitute_off: string | null;

  creator_player_id: number | null;
  shooter_player_id: number | null;
  defender_player_id: number | null;
  goalkeeper_id: number | null;
  substitute_on_id: number | null;
  substitute_off_id: number | null;

  club_name: string | null;
}

export interface ReplayScene {
  action_id: number;
  match_minute: number;
  kind: string;
  club_name: string | null;
  player_name: string | null;
}

export interface ReplayScheduleItem {
  scene: ReplayScene;
  replay_seconds: number;
}

export interface ScoreSnapshot {
  match_minute: number;
  home_score: number;
  away_score: number;
}

export interface ReplayTacticTimelineItem {
  time?: number;
  formation_id?: number | null;
  formation_name?: string | null;
  play_style?: string | null;
  play_style_int?: number | null;
  situation?: number | null;
  goal_margin?: number | null;
}

export interface ReplayTacticState {
  formation: string | null;
  formation_id: number | null;
  play_style: string | null;
  changed: boolean;
  change_minute: number | null;
  timeline: ReplayTacticTimelineItem[];
}

export interface ReplayTacticsState {
  home: ReplayTacticState;
  away: ReplayTacticState;
}

export interface ReplayState {
  replay_mode: ReplayMode;
  elapsed_seconds: number;
  match_minute: number;
  current_scene: ReplayScheduleItem | null;
  visible_scenes: ReplayScheduleItem[];
  home_score: number;
  away_score: number;
  tactics: ReplayTacticsState;
}