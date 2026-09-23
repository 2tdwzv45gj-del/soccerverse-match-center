export type CommentaryEvent = {
  comm_sub_event_id?: number;
  comm_event_id?: number;
  time?: number;
  category?: string;
  player_one_id?: number | null;
  player_one_name?: string | null;
  player_two_id?: number | null;
  player_two_name?: string | null;
  club_one_id?: number | null;
  club_one_name?: string | null;
  event_player_id?: number | null;
  event_player_name?: string | null;
};

export type LiveCommentaryItem = {
  id: number;
  time: number;
  category: string;
  icon: string;
  label: string;
  player: string;
  secondary: string;
  club: string;
};

const labels: Record<string, { icon: string; label: string }> = {
  GOAL: { icon: "⚽", label: "GOAL!" },
  SAVE: { icon: "🧤", label: "PARATA" },
  OFFTARGET: { icon: "🎯", label: "TIRO FUORI" },
  CHANCE: { icon: "🔥", label: "OCCASIONE" },
  ASSISTEDCHANCE: { icon: "🅰️", label: "ASSIST" },
  TACKLE: { icon: "🛡️", label: "CONTRASTO" },
  FOUL: { icon: "⚠️", label: "FALLO" },
  SHOT: { icon: "🎯", label: "TIRO" },
  CHANGETACTIC: { icon: "🔄", label: "CAMBIO TATTICO" },
};

function playerFor(event: CommentaryEvent) {
  return event.event_player_name || event.player_one_name || event.player_two_name || "";
}

function buildItem(group: CommentaryEvent[]): LiveCommentaryItem {
  const sorted = [...group].sort((a, b) => Number(a.comm_sub_event_id ?? 0) - Number(b.comm_sub_event_id ?? 0));
  const categories = sorted.map((event) => String(event.category ?? "").toUpperCase());
  const primary = categories.includes("GOAL") ? "GOAL" : categories.includes("SAVE") ? "SAVE" : categories.includes("OFFTARGET") ? "OFFTARGET" : categories.includes("TACKLE") ? "TACKLE" : categories.includes("FOUL") ? "FOUL" : categories.includes("SHOT") ? "SHOT" : categories.includes("CHANCE") ? "CHANCE" : categories.includes("CHANGETACTIC") ? "CHANGETACTIC" : categories[0] || "ACTION";
  const meta = labels[primary] || { icon: "•", label: primary.replaceAll("_", " ") };
  const mainEvent = sorted.find((event) => ["GOAL", "SAVE", "OFFTARGET", "TACKLE", "FOUL", "SHOT", "CHANCE", "CHANGETACTIC"].includes(String(event.category ?? "").toUpperCase())) || sorted[0];
  const assistEvent = sorted.find((event) => String(event.category ?? "").toUpperCase() === "ASSISTEDCHANCE");
  const player = playerFor(mainEvent);
  const secondary = assistEvent?.player_one_name && assistEvent.player_one_name !== player ? "Assist: " + assistEvent.player_one_name : "";
  return { id: Number(sorted[0]?.comm_event_id ?? sorted[0]?.comm_sub_event_id ?? 0), time: Number(sorted[0]?.time ?? 0), category: primary, icon: meta.icon, label: meta.label, player, secondary, club: mainEvent?.club_one_name || assistEvent?.club_one_name || "" };
}

export function buildLiveCommentary(events: CommentaryEvent[]): LiveCommentaryItem[] {
  const groups = new Map<number, CommentaryEvent[]>();
  for (const event of events) {
    const id = Number(event.comm_event_id ?? event.comm_sub_event_id ?? 0);
    const group = groups.get(id) || [];
    group.push(event);
    groups.set(id, group);
  }
  return Array.from(groups.values()).map(buildItem).sort((a, b) => a.time - b.time || a.id - b.id);
}

export function getCurrentCommentary(items: LiveCommentaryItem[], minute: number): LiveCommentaryItem | null {
  let current: LiveCommentaryItem | null = null;
  for (const item of items) {
    if (item.time <= minute) current = item;
    else break;
  }
  return current;
}
