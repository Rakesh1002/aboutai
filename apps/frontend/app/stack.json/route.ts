import { NextResponse } from "next/server";
import { getStack } from "@/lib/content";

export const dynamic = "force-static";

export function GET() {
  return NextResponse.json(getStack(), {
    headers: {
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  });
}
