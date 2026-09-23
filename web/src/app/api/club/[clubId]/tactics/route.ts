import { NextResponse } from "next/server";

const MCP_URL = "https://mcp.soccerverse.io/mcp";

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

    const tactics = await mcpCall("get_club_tactics", {
      club_id: Number(clubId),
    });

    return NextResponse.json({
      clubId: Number(clubId),
      tactics,
    });
  } catch (error) {
    console.error(error);

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : "Unable to load club tactics",
      },
      { status: 500 }
    );
  }
}
