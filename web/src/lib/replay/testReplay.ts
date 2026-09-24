import {
  MatchReplayController,
} from "./matchReplayController";

async function main() {
  const response = await fetch(
    "http://localhost:3000/api/match/427215",
  );

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status}`,
    );
  }

  const data = await response.json();

  const controller =
    new MatchReplayController(
      {
        fixture: data.fixture,
        events: data.events,
        commentary: data.commentary,
        injuries: data.injuries ?? [],
        startingPlayers: data.startingPlayers ?? [],
        tactics: data.tactics ?? undefined,
      },
      "M3",
    );

  const checkpoints = [
    92,
    94,
    130,
    132,
    146,
    148,
    154,
    156,
    162,
    164,
  ];

  for (const seconds of checkpoints) {
    const state =
      controller.setElapsedSeconds(
        seconds,
      );

    console.log(
      JSON.stringify({
        replaySeconds:
          seconds,
        matchMinute:
          state.match_minute,
        score:
          `${state.home_score}-${state.away_score}`,
        visibleScenes:
          state.visible_scenes.length,
        currentKind:
          state.current_kind,
        currentActionId:
          state.current_action_id,
        tactics: {
          home: state.tactics.home,
          away: state.tactics.away,
        },
      }),
    );
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});