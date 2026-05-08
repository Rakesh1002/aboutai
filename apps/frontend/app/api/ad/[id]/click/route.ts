import { NextRequest, NextResponse } from "next/server";
import { getAdById } from "@/lib/ads";

export const dynamic = "force-dynamic";

function resolveDestination(
  rawUrl: string,
  adId: string,
  origin: string
): URL {
  if (rawUrl.startsWith("/")) {
    return new URL(rawUrl, origin);
  }
  try {
    const u = new URL(rawUrl);
    if (!u.searchParams.has("utm_source")) {
      u.searchParams.set("utm_source", "theaidaily");
    }
    if (!u.searchParams.has("utm_medium")) {
      u.searchParams.set("utm_medium", "edge_rail");
    }
    if (!u.searchParams.has("utm_campaign")) {
      u.searchParams.set("utm_campaign", adId);
    }
    return u;
  } catch {
    return new URL("/", origin);
  }
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const origin = new URL(req.url).origin;
  const ad = getAdById(id);
  if (!ad) {
    return NextResponse.redirect(new URL("/", origin), 302);
  }
  return NextResponse.redirect(resolveDestination(ad.url, ad.id, origin), 302);
}
