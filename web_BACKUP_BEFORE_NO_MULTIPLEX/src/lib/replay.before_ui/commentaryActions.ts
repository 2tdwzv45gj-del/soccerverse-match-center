import type {
  CommentaryAction,
  CommentarySubEvent,
} from "./types";

export function groupCommentaryActions(
  events: CommentarySubEvent[],
): CommentaryAction[] {
  const groups = new Map<number, CommentarySubEvent[]>();

  for (const event of events) {
    const group = groups.get(event.comm_event_id);

    if (group) {
      group.push(event);
    } else {
      groups.set(event.comm_event_id, [event]);
    }
  }

  const actions: CommentaryAction[] = [];

  for (const [commEventId, subEvents] of groups) {
    const ordered = [...subEvents].sort(
      (a, b) => a.comm_sub_event_id - b.comm_sub_event_id,
    );

    const first = ordered[0];

    actions.push({
      comm_event_id: commEventId,
      time: first.time,
      club_one_id: first.club_one_id ?? null,
      club_one_name: first.club_one_name ?? null,
      sub_events: ordered,
    });
  }

  return actions.sort(
    (a, b) =>
      a.time - b.time ||
      a.comm_event_id - b.comm_event_id,
  );
}