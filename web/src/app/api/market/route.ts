import { NextResponse } from "next/server";

export const revalidate = 30;

async function getSoccerverseMarket() {
  const response = await fetch("https://mcp.soccerverse.io/mcp", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "tools/call",
      params: {
        name: "get_market_data",
        arguments: {},
      },
    }),
    next: { revalidate: 30 },
  });

  if (!response.ok) {
    throw new Error(`Soccerverse MCP HTTP ${response.status}`);
  }

  const rpc = await response.json();
  const text = rpc?.result?.content?.find(
    (item: any) => item?.type === "text"
  )?.text;

  if (!text) {
    throw new Error("Soccerverse MCP returned no market data");
  }

  return JSON.parse(text);
}

export async function GET() {
  try {
    const [market, cryptoResponse] = await Promise.all([
      getSoccerverseMarket(),
      fetch(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum%2Cpolygon-ecosystem-token&vs_currencies=usd",
        {
          next: { revalidate: 30 },
        }
      ),
    ]);

    if (!cryptoResponse.ok) {
      throw new Error(`CoinGecko HTTP ${cryptoResponse.status}`);
    }

    const crypto = await cryptoResponse.json();

    return NextResponse.json({
      svc: market?.SVC2USDC ?? null,
      eth: crypto?.ethereum?.usd ?? null,
      pol: crypto?.["polygon-ecosystem-token"]?.usd ?? null,
      updatedAt: Date.now(),
    });
  } catch (error) {
    console.error("MARKET API ERROR:", error);

    return NextResponse.json(
      {
        svc: null,
        eth: null,
        pol: null,
        updatedAt: Date.now(),
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 200 }
    );
  }
}
