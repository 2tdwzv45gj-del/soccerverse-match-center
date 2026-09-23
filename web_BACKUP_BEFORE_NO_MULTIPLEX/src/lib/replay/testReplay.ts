import {
  MatchReplayController,
} from "./matchReplayController";

async function main() {
  const response = await fetch(
    "http://localhost:3000/api/match/334245",
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
      },
      "M3",
    );

  const checkpoints = [
    0,
    60,
    90,
    120,
    150,
    180,
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
      }),
    );
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});