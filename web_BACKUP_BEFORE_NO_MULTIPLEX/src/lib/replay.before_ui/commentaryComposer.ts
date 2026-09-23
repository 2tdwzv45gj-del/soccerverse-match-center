import type {
  CommentaryAction,
  NarrativeIntent,
} from "./types";

function findPlayerOne(
  action: CommentaryAction,
  category: string,
): string | null {
  for (const event of action.sub_events) {
    if (event.category === category) {
      return event.player_one_name ?? null;
    }
  }

  return null;
}

function findPlayerTwo(
  action: CommentaryAction,
  category: string,
): string | null {
  for (const event of action.sub_events) {
    if (event.category === category) {
      return event.player_two_name ?? null;
    }
  }

  return null;
}

function findPlayerOneId(
  action: CommentaryAction,
  category: string,
): number | null {
  for (const event of action.sub_events) {
    if (event.category === category) {
      return event.player_one_id ?? null;
    }
  }

  return null;
}

function findPlayerTwoId(
  action: CommentaryAction,
  category: string,
): number | null {
  for (const event of action.sub_events) {
    if (event.category === category) {
      return event.player_two_id ?? null;
    }
  }

  return null;
}

export function composeAction(
  action: CommentaryAction,
): NarrativeIntent {
  const categories = action.sub_events.map(
    (event) => event.category,
  );

  let kind = "other";

  let creator: string | null = null;
  let shooter: string | null = null;
  let defender: string | null = null;
  let goalkeeper: string | null = null;
  let substituteOn: string | null = null;
  let substituteOff: string | null = null;

  if (categories.includes("GOAL")) {
    kind = "goal";

    creator = findPlayerOne(action, "CHANCE");
    shooter = findPlayerOne(action, "GOAL");

    if (shooter === null) {
      shooter = findPlayerOne(action, "SHOT");
    }

    if (shooter === null) {
      shooter = creator;
    }
  } else if (categories.includes("SAVE")) {
    kind = "chance_saved";

    creator = findPlayerOne(action, "ASSISTEDCHANCE");
    shooter = findPlayerTwo(action, "ASSISTEDCHANCE");

    if (shooter === null) {
      shooter = findPlayerOne(action, "SHOT");
    }

    if (shooter === null) {
      shooter = findPlayerOne(action, "CHANCE");
    }

    goalkeeper = findPlayerOne(action, "SAVE");
  } else if (categories.includes("OFFTARGET")) {
    kind = "chance_offtarget";

    creator = findPlayerOne(action, "ASSISTEDCHANCE");
    shooter = findPlayerTwo(action, "ASSISTEDCHANCE");

    if (shooter === null) {
      shooter = findPlayerOne(action, "SHOT");
    }

    if (shooter === null) {
      shooter = findPlayerOne(action, "CHANCE");
    }
  } else if (categories.includes("TACKLE")) {
    kind = "chance_tackled";

    creator = findPlayerOne(action, "ASSISTEDCHANCE");
    shooter = findPlayerTwo(action, "ASSISTEDCHANCE");

    defender = findPlayerOne(action, "TACKLE");

    if (shooter === null) {
      shooter = findPlayerOne(action, "CHANCE");
    }
  } else if (categories.includes("SUB")) {
    kind = "substitution";

    substituteOn = findPlayerOne(action, "SUB");
    substituteOff = findPlayerTwo(action, "SUB");
  } else if (categories.includes("SHOT")) {
    kind = "shot";
    shooter = findPlayerOne(action, "SHOT");
  }

  return {
    action_id: action.comm_event_id,
    minute: action.time,
    kind,

    creator_player: creator,
    shooter_player: shooter,
    defender_player: defender,
    goalkeeper,
    substitute_on: substituteOn,
    substitute_off: substituteOff,

    creator_player_id:
      findPlayerOneId(action, "ASSISTEDCHANCE") ??
      findPlayerOneId(action, "CHANCE"),

    shooter_player_id:
      findPlayerOneId(action, "GOAL") ??
      findPlayerTwoId(action, "ASSISTEDCHANCE") ??
      findPlayerOneId(action, "SHOT") ??
      findPlayerOneId(action, "CHANCE"),

    defender_player_id:
      findPlayerOneId(action, "TACKLE"),

    goalkeeper_id:
      findPlayerOneId(action, "SAVE"),

    substitute_on_id:
      findPlayerOneId(action, "SUB"),

    substitute_off_id:
      findPlayerTwoId(action, "SUB"),

    club_name: action.club_one_name,
  };
}

export function composeActions(
  actions: CommentaryAction[],
): NarrativeIntent[] {
  return actions.map(composeAction);
}