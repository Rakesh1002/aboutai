import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/cf";
import { checkAggregatorAuth } from "@/lib/aggregator/auth";
import {
  addSource,
  getEnabledSources,
  seedSourcesIfEmpty,
  setSourceEnabled,
  type SourceRow,
} from "@/lib/aggregator/sources";

export const dynamic = "force-dynamic";
export const runtime = "edge";

function withDB() {
  return getEnv() as unknown as { DB: D1Database };
}

export async function GET(req: NextRequest) {
  const auth = checkAggregatorAuth(req, "cron");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  const db = withDB().DB;
  await seedSourcesIfEmpty(db);
  // Include disabled rows for visibility.
  const all = await db
    .prepare(
      `SELECT id, name, url, kind, region, weight, enabled,
              last_fetched_at, last_status, last_error, created_at
       FROM aggregator_sources ORDER BY weight DESC, name ASC`
    )
    .all<SourceRow>();
  const enabled = await getEnabledSources(db);
  return NextResponse.json({
    ok: true,
    enabledCount: enabled.length,
    totalCount: all.results.length,
    sources: all.results,
  });
}

interface PostRequest {
  action?: "add" | "enable" | "disable";
  id?: string;
  name?: string;
  url?: string;
  kind?: "rss" | "atom";
  region?: "india" | "global";
  weight?: number;
}

export async function POST(req: NextRequest) {
  const auth = checkAggregatorAuth(req, "admin");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  let body: PostRequest;
  try {
    body = (await req.json()) as PostRequest;
  } catch {
    return NextResponse.json({ ok: false, error: "bad_json" }, { status: 400 });
  }

  const db = withDB().DB;
  switch (body.action) {
    case "add": {
      if (
        !body.name ||
        !body.url ||
        !body.kind ||
        !body.region ||
        typeof body.weight !== "number"
      ) {
        return NextResponse.json(
          { ok: false, error: "missing_fields" },
          { status: 400 }
        );
      }
      const id = await addSource(db, {
        id: body.id,
        name: body.name,
        url: body.url,
        kind: body.kind,
        region: body.region,
        weight: body.weight,
      });
      return NextResponse.json({ ok: true, id });
    }
    case "enable":
    case "disable": {
      if (!body.id) {
        return NextResponse.json(
          { ok: false, error: "missing_id" },
          { status: 400 }
        );
      }
      await setSourceEnabled(db, body.id, body.action === "enable");
      return NextResponse.json({ ok: true });
    }
    default:
      return NextResponse.json(
        { ok: false, error: "bad_action" },
        { status: 400 }
      );
  }
}
