import { NextResponse } from "next/server";
import fs from "node:fs";
import path from "node:path";

type Club = {
  id: string;
  n?: string;
  rgb?: string;
};

function loadDatapack() {
  const datapackPath = path.join(
    process.cwd(), "..", "data", "raw", "datapack", "rincon_s4.json"
  );
  return JSON.parse(fs.readFileSync(datapackPath, "utf-8")).PackData;
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ clubId: string }> }
) {
  try {
    const { clubId } = await context.params;

    if (!/^\d+$/.test(clubId) || Number(clubId) <= 0) {
      return NextResponse.json({ error: "Invalid club ID" }, { status: 400 });
    }

    const pack = loadDatapack();
    const club = pack.ClubData.C.find(
      (item: Club) => String(item.id) === clubId
    );

    if (!club) {
      return NextResponse.json(
        { error: "Club " + clubId + " not found" },
        { status: 404 }
      );
    }

    const rgb = club.rgb
      ? club.rgb.split(",").map((value: string) => Number(value.trim()))
      : null;

    return NextResponse.json({
      id: Number(club.id),
      name: club.n || "Club " + club.id,
      colors: rgb,
      logo:
        pack.ClubData.baseImageUrl.replace(/\/$/, "") +
        "/" + club.id + ".png"
    });
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      { error: "Failed to load club data" },
      { status: 500 }
    );
  }
}
