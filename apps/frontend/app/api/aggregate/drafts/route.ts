import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/cf";
import { checkAggregatorAuth } from "@/lib/aggregator/auth";
import { listDrafts } from "@/lib/aggregator/pipeline";

export const dynamic = "force-dynamic";
export const runtime = "edge";

export async function GET(req: NextRequest) {
  const auth = checkAggregatorAuth(req, "cron");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  const env = getEnv() as unknown as { DB: D1Database };
  const limitParam = req.nextUrl.searchParams.get("limit");
  const limit = Math.min(Math.max(parseInt(limitParam ?? "30", 10) || 30, 1), 90);
  const rows = await listDrafts(env.DB, limit);
  return NextResponse.json({
    ok: true,
    count: rows.length,
    drafts: rows.map((r) => ({
      date: r.date,
      status: r.status,
      generator: r.generator,
      model: r.generator_model,
      candidateCount: r.candidate_count,
      shortlistCount: r.shortlist_count,
      generatedAt: r.generated_at,
      reviewedAt: r.reviewed_at,
    })),
  });
}
