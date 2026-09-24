import { NextResponse } from "next/server";

export const revalidate = 30;

export async function GET() {
  try {
    const [soccerverseResponse, cryptoResponse] = await Promise.all([
      fetch("https://services.soccerverse.com/api/ticker", {
        next: { revalidate: 30 },
      }),
      fetch(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum%2Cpolygon-ecosystem-token&vs_currencies=usd",
        {
          next: { revalidate: 30 },
        }
      ),
    ]);

    if (!soccerverseResponse.ok) {
      throw new Error(`Soccerverse HTTP ${soccerverseResponse.status}`);
    }

    if (!cryptoResponse.ok) {
      throw new Error(`CoinGecko HTTP ${cryptoResponse.status}`);
    }

    const soccerverse = await soccerverseResponse.json();
    const crypto = await cryptoResponse.json();

    return NextResponse.json({
      svc: soccerverse?.svc_usdc ?? soccerverse?.svc_price ?? null,
      eth: crypto?.ethereum?.usd ?? null,
      pol: crypto?.["polygon-ecosystem-token"]?.usd ?? null,
      updatedAt: Date.now(),
      debug: {
        soccerverseKeys: Object.keys(soccerverse ?? {}),
        soccerverseData: soccerverse,
        coinGeckoData: crypto,
      },
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
