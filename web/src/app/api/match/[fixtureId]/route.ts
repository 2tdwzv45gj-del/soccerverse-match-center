import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

const MCP_URL = "https://mcp.soccerverse.io/mcp";
const REST_URL = "https://services.soccerverse.com/api";

const STADIUM_PACK_PATH = path.join(
  process.cwd(),
  "..",
  "data",
  "raw",
  "datapack",
  "rincon_s4.json"
);

async function getPlayerNames() {
  const raw = await readFile(STADIUM_PACK_PATH, "utf8");
  const pack = JSON.parse(raw);
  const playerData = pack?.PackData?.PlayerData;
  const players = Array.isArray(playerData)
    ? playerData
    : playerData?.P ?? playerData?.data ?? playerData?.items ?? [];

  return new Map(
    players
      .filter((player: any) => player?.id != null)
      .map((player: any) => [
        Number(player.id),
        [player.f, player.s].filter(Boolean).join(" "),
      ])
      .filter(([, name]: any) => Boolean(name))
  );
}


async function analyseClub(clubId: number) {
  return mcpCall("analyse_club", { club_id: clubId });
}

async function getStadium(stadiumId: unknown) {
  if (stadiumId === undefined || stadiumId === null || stadiumId === "") {
    return null;
  }

  const raw = await readFile(STADIUM_PACK_PATH, "utf8");
  const pack = JSON.parse(raw);
  const stadiumData = pack?.PackData?.StadiumData;

  const stadiums = Array.isArray(stadiumData)
    ? stadiumData
    : stadiumData?.S ?? stadiumData?.data ?? stadiumData?.items ?? [];

  const stadium = stadiums.find(
    (item: any) => String(item?.id) === String(stadiumId)
  );

  if (!stadium) {
    return null;
  }

  const baseImageUrl =
    stadiumData?.baseImageUrl ||
    "https://pack.elrincondeldt.com/sv/photos/venues/";

  return {
    id: Number(stadium.id),
    name: stadium.n || stadium.name || "SOCCERVERSE STADIUM",
    image: baseImageUrl.endsWith("/")
      ? baseImageUrl + String(stadium.id) + ".png"
      : baseImageUrl + "/" + String(stadium.id) + ".png",
  };
}


async function mcpCall(
  toolName: string,
  arguments_: Record<string, unknown>
) {
  const response = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: {
        name: toolName,
        arguments: arguments_,
      },
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("MCP request failed: " + response.status);
  }

  const text = await response.text();

  for (const line of text.split("\n")) {
    if (line.startsWith("data:")) {
      try {
        return extractResult(JSON.parse(line.slice(5).trim()));
      } catch {}
    }
  }

  try {
    return extractResult(JSON.parse(text));
  } catch {
    throw new Error("Invalid MCP response");
  }
}

function extractResult(payload: any): any {
  const content = payload?.result?.content;

  if (Array.isArray(content)) {
    const item = content.find(
      (entry: any) => entry?.type === "text"
    );

    if (item?.text) {
      try {
        return JSON.parse(item.text);
      } catch {
        return item.text;
      }
    }
  }

  return payload?.result ?? payload;
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ fixtureId: string }> }
) {
  try {
    const { fixtureId } = await context.params;

    if (!/^\d+$/.test(fixtureId) || Number(fixtureId) <= 0) {
      return NextResponse.json(
        { error: "Invalid fixture ID" },
        { status: 400 }
      );
    }

    const id = Number(fixtureId);

    const [fixture, events, commentary, substitutions, fixturePlayerData] =
      await Promise.all([
        mcpCall("get_fixture", { fixture_id: id }),
        mcpCall("get_match_events", { fixture_id: id }),
        mcpCall("get_match_commentary", { fixture_id: id }),
        mcpCall("get_match_subs", { fixture_id: id }),
        mcpCall("get_fixture_player_data", { fixture_id: id }),
      ]);

    const [homeAnalysis, awayAnalysis] = await Promise.all([analyseClub(Number(fixture?.home_club)), analyseClub(Number(fixture?.away_club))]);

  const findFixtureTactics = (analysis: any) => {
    const fixtureTactics =
      analysis?.recent_results?.find(
        (item: any) => Number(item?.fixture_id) === id
      ) ?? null;

    const currentTactics = analysis?.current_tactics ?? null;

    return fixtureTactics
      ? {
          ...fixtureTactics,
          situational_styles: Array.isArray(currentTactics?.situational_styles)
            ? currentTactics.situational_styles
            : [],
          planned_substitutions: Array.isArray(currentTactics?.planned_substitutions)
            ? currentTactics.planned_substitutions
            : [],
        }
      : null;
  };

  const homeTactics = findFixtureTactics(homeAnalysis);
  const awayTactics = findFixtureTactics(awayAnalysis);

    const stadium = await getStadium(fixture?.stadium_id ?? fixture?.stadium ?? null);

    const playerNames = await getPlayerNames();

    const injuries = (Array.isArray(fixturePlayerData) ? fixturePlayerData : [])
      .filter((player: any) => Number(player?.injuries ?? 0) > 0)
      .map((player: any) => ({
        minute: Number(player?.time_finished ?? 0),
        player_id: Number(player?.player_id),
        player_name: playerNames.get(Number(player?.player_id)) ?? player?.player_name ?? `Player #${player?.player_id}`,
        club_id: Number(player?.club_id),
        club_name: player?.club_name ?? "",
        side: player?.side ?? "",
      }));

    const commentaryItems = Array.isArray(commentary)
      ? commentary
      : commentary?.commentary ?? [];

    // Normalize ONLY GOAL events using fixture player data.
    // Soccerverse may occasionally return an incorrect club_id on a GOAL.
    // GOALCANCELLED and every other event are intentionally left untouched.
    const fixturePlayerClubById = new Map<number, number>();

    if (Array.isArray(fixturePlayerData)) {
      for (const player of fixturePlayerData) {
        const playerId = Number(player?.player_id);
        const clubId = Number(player?.club_id);

        if (
          Number.isFinite(playerId) &&
          playerId > 0 &&
          Number.isFinite(clubId) &&
          clubId > 0
        ) {
          fixturePlayerClubById.set(playerId, clubId);
        }
      }
    }

    const normalizedEvents = Array.isArray(events)
      ? events.map((event: any) => {
          const eventType = String(event?.event_type ?? "").toUpperCase();

          // IMPORTANT:
          // Only GOAL events are normalized.
          // GOALCANCELLED remains completely unchanged.
          if (eventType !== "GOAL") {
            return event;
          }

          const playerId = Number(
            event?.player_id ?? event?.event_player_id
          );

          const playerClubId = fixturePlayerClubById.get(playerId);

          if (playerClubId === undefined) {
            return event;
          }

          const eventClubId = Number(event?.club_id);

          if (eventClubId !== playerClubId) {
            console.log(
              "[GOAL CLUB FIX]",
              "fixture=" + id,
              "match_event_id=" + String(event?.match_event_id ?? ""),
              "player_id=" + String(playerId),
              "old_club_id=" + String(eventClubId),
              "new_club_id=" + String(playerClubId)
            );

            return {
              ...event,
              club_id: playerClubId,
            };
          }

          return event;
        })
      : [];

  return NextResponse.json({
      fixtureId: id,
      fixture,
      stadium,
      events: normalizedEvents,
      commentary: Array.isArray(commentaryItems)
        ? commentaryItems
        : [],
      substitutions: Array.isArray(substitutions)
        ? substitutions
        : [],
      tactics: { home: homeTactics, away: awayTactics },
      injuries,
      startingPlayers: (Array.isArray(fixturePlayerData) ? fixturePlayerData : []).filter((player: any) => Number(player?.time_started ?? -1) === 0).sort((a: any, b: any) => Number(a?.start_ix ?? 999) - Number(b?.start_ix ?? 999)).map((player: any) => ({ player_id: Number(player?.player_id), player_name: playerNames.get(Number(player?.player_id)) ?? player?.player_name ?? `Player #${player?.player_id}`, side: player?.side ?? ``, club_id: Number(player?.club_id), start_ix: Number(player?.start_ix ?? 0) })),
    });
  } catch (error) {
    console.error(error);

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "Failed to load match data",
      },
      { status: 500 }
    );
  }
}
