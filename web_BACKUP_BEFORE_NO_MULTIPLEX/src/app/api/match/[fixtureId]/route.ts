import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

const MCP_URL = "https://mcp.soccerverse.io/mcp";

const STADIUM_PACK_PATH = path.join(
  process.cwd(),
  "..",
  "data",
  "raw",
  "datapack",
  "rincon_s4.json"
);

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

    const [fixture, events, commentary, substitutions] =
      await Promise.all([
        mcpCall("get_fixture", { fixture_id: id }),
        mcpCall("get_match_events", { fixture_id: id }),
        mcpCall("get_match_commentary", { fixture_id: id }),
        mcpCall("get_match_subs", { fixture_id: id }),
      ]);

    const stadium = await getStadium(fixture?.stadium_id ?? fixture?.stadium ?? null);

    const commentaryItems = Array.isArray(commentary)
      ? commentary
      : commentary?.commentary ?? [];

    return NextResponse.json({
      fixtureId: id,
      fixture,
      stadium,
      events: Array.isArray(events) ? events : [],
      commentary: Array.isArray(commentaryItems)
        ? commentaryItems
        : [],
      substitutions: Array.isArray(substitutions)
        ? substitutions
        : [],
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
