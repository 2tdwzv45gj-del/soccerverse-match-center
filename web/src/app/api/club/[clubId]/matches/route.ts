import { NextResponse } from "next/server";

const MCP_URL = "https://mcp.soccerverse.io/mcp";

function loadDatapack() {
  const fs = require("node:fs");
  const path = require("node:path");
  const datapackPath = path.join(
    process.cwd(), "..", "data", "raw", "datapack", "rincon_s4.json"
  );
  return JSON.parse(fs.readFileSync(datapackPath, "utf-8")).PackData;
}

function getClubIdentity(pack: any, clubId: number, fallbackName: string) {
  const club = pack.ClubData.C.find(
    (item: any) => String(item.id) === String(clubId)
  );

  if (!club) {
    return {
      id: clubId,
      name: fallbackName,
      logo: null,
      colors: null,
    };
  }

  return {
    id: clubId,
    name: club.n || fallbackName,
    logo:
      (pack.ClubData.baseImageUrl.endsWith("/") ? pack.ClubData.baseImageUrl.slice(0, -1) : pack.ClubData.baseImageUrl) +
      "/" + club.id + ".png",
    colors: club.rgb
      ? club.rgb.split(",").map((value: string) => Number(value.trim()))
      : null,
  };
}

async function mcpCall(toolName: string, arguments_: Record<string, unknown>) {
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
        const parsed = JSON.parse(line.slice(5).trim());
        return extractResult(parsed);
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
    const item = content.find((entry: any) => entry?.type === "text");

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
  context: { params: Promise<{ clubId: string }> }
) {
  try {
    const { clubId } = await context.params;

    if (!/^\d+$/.test(clubId) || Number(clubId) <= 0) {
      return NextResponse.json(
        { error: "Invalid club ID" },
        { status: 400 }
      );
    }

    const schedule = await mcpCall("get_club_schedule", {
      club_id: Number(clubId),
    });

    const pack = loadDatapack();

    if (!Array.isArray(schedule)) {
      throw new Error("Invalid schedule response");
    }

    const matches = schedule
      .map((item: any) => ({
        fixtureId: Number(item.fixture_id),
        homeClubId: Number(item.home_club),
        awayClubId: Number(item.away_club),
        home: getClubIdentity(
          pack,
          Number(item.home_club),
          String(item.home_club_name ?? item.home_club)
        ),
        away: getClubIdentity(
          pack,
          Number(item.away_club),
          String(item.away_club_name ?? item.away_club)
        ),
        homeGoals: Number(item.home_goals ?? 0),
        awayGoals: Number(item.away_goals ?? 0),
        played: Boolean(item.played),
        datetime: String(item.datetime ?? ""),
        competition: String(
          item.comp_name ?? item.league_name ?? ""
        ),
      }))
      .sort((a, b) => {
        const dateA = Date.parse(a.datetime);
        const dateB = Date.parse(b.datetime);
        return dateA - dateB || a.fixtureId - b.fixtureId;
      });

    return NextResponse.json({
      clubId: Number(clubId),
      matches,
    });
  } catch (error) {
    console.error(error);

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to load matches" },
      { status: 500 }
    );
  }
}
