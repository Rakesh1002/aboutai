import { NextRequest, NextResponse } from "next/server";
import { getEnv } from "@/lib/cf";
import { checkAggregatorAuth } from "@/lib/aggregator/auth";
import { runPipeline, todayInIST } from "@/lib/aggregator/pipeline";

export const dynamic = "force-dynamic";
export const runtime = "edge";

interface RunRequest {
  date?: string;
  shortlistSize?: number;
  dryRun?: boolean;
  skipPersist?: boolean;
}

function parseDate(input: unknown): string {
  if (typeof input === "string" && /^\d{4}-\d{2}-\d{2}$/.test(input)) {
    return input;
  }
  return todayInIST();
}

export async function POST(req: NextRequest) {
  const auth = checkAggregatorAuth(req, "cron");
  if (!auth.ok) {
    return NextResponse.json(
      { ok: false, error: "unauthorized", reason: auth.reason },
      { status: 401 }
    );
  }

  let body: RunRequest = {};
  try {
    if (req.headers.get("content-length") !== "0") {
      body = (await req.json()) as RunRequest;
    }
  } catch {
    body = {};
  }

  const env = getEnv() as unknown as {
    DB: D1Database;
    ANTHROPIC_API_KEY?: string;
    ANTHROPIC_MODEL?: string;
  };

  try {
    const result = await runPipeline(env, {
      date: parseDate(body.date),
      shortlistSize: body.shortlistSize,
      dryRun: !!body.dryRun,
      skipPersist: !!body.skipPersist,
    });
    return NextResponse.json({
      ok: true,
      date: result.date,
      status: result.status,
      candidateCount: result.candidateCount,
      shortlistCount: result.shortlistCount,
      fetchSummaries: result.fetchSummaries,
      errors: result.errors,
      // Only return draft + raw on dry runs; otherwise look it up via /draft.
      ...(body.dryRun
        ? { shortlist: result.shortlist }
        : {}),
      ...(result.daily ? { daily: result.daily } : {}),
      ...(result.model ? { model: result.model } : {}),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "unknown";
    return NextResponse.json(
      { ok: false, error: "pipeline_failed", message: msg },
      { status: 500 }
    );
  }
}
