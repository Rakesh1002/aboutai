import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/cf";
import { checkAggregatorAuth } from "@/lib/aggregator/auth";
import { getDraft, setDraftStatus } from "@/lib/aggregator/pipeline";
import { renderDailyModule, renderRegistrationHint } from "@/lib/aggregator/render";
import type { Daily } from "@/lib/content";

export const dynamic = "force-dynamic";
export const runtime = "edge";

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function withDB() {
  return getEnv() as unknown as { DB: D1Database };
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ date: string }> }
) {
  const auth = checkAggregatorAuth(req, "cron");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  const { date } = await params;
  if (!DATE_RE.test(date)) {
    return NextResponse.json({ ok: false, error: "bad_date" }, { status: 400 });
  }

  const row = await getDraft(withDB().DB, date);
  if (!row) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }

  let daily: Daily;
  try {
    daily = JSON.parse(row.payload) as Daily;
  } catch {
    return NextResponse.json(
      { ok: false, error: "draft_corrupt" },
      { status: 500 }
    );
  }

  const format = req.nextUrl.searchParams.get("format") ?? "json";
  if (format === "ts" || format === "module") {
    const body =
      renderDailyModule(daily) +
      "\n" +
      renderRegistrationHint(date) +
      "\n";
    return new NextResponse(body, {
      status: 200,
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  }

  return NextResponse.json({
    ok: true,
    date: row.date,
    status: row.status,
    generator: row.generator,
    model: row.generator_model,
    candidateCount: row.candidate_count,
    shortlistCount: row.shortlist_count,
    generatedAt: row.generated_at,
    reviewedAt: row.reviewed_at,
    notes: row.notes,
    daily,
  });
}

interface PatchRequest {
  status?: "draft" | "reviewed" | "published" | "discarded";
  notes?: string;
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ date: string }> }
) {
  const auth = checkAggregatorAuth(req, "admin");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  const { date } = await params;
  if (!DATE_RE.test(date)) {
    return NextResponse.json({ ok: false, error: "bad_date" }, { status: 400 });
  }

  let body: PatchRequest;
  try {
    body = (await req.json()) as PatchRequest;
  } catch {
    return NextResponse.json(
      { ok: false, error: "bad_json" },
      { status: 400 }
    );
  }
  if (
    !body.status ||
    !["draft", "reviewed", "published", "discarded"].includes(body.status)
  ) {
    return NextResponse.json(
      { ok: false, error: "bad_status" },
      { status: 400 }
    );
  }

  const updated = await setDraftStatus(
    withDB().DB,
    date,
    body.status,
    body.notes
  );
  if (!updated) {
    return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  }
  return NextResponse.json({ ok: true, date, status: body.status });
}
