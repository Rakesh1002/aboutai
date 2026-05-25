import { now } from "@/lib/cf";
import type { Daily } from "@/lib/content";
import { fetchAllSources, type FetchSummary } from "./fetch";
import { draftDaily } from "./draft";
import {
  dedupeAndShortlist,
  recordSeen,
  scoreItems,
  type ScoredItem,
} from "./score";
import {
  getEnabledSources,
  recordSourceFetch,
  seedSourcesIfEmpty,
} from "./sources";

export interface PipelineEnv {
  DB: D1Database;
  ANTHROPIC_API_KEY?: string;
  ANTHROPIC_MODEL?: string;
}

export interface PipelineOptions {
  date: string; // YYYY-MM-DD in IST
  shortlistSize?: number;
  dryRun?: boolean; // skip LLM call + DB writes
  skipPersist?: boolean; // skip DB writes only
}

export interface PipelineResult {
  date: string;
  status: "drafted" | "dry-run" | "no-candidates";
  fetchSummaries: FetchSummary[];
  candidateCount: number;
  shortlistCount: number;
  shortlist: ScoredItem[];
  daily?: Daily;
  model?: string;
  generator?: string;
  rawResponse?: string;
  errors: string[];
}

const DEFAULT_SHORTLIST = 8;

export async function runPipeline(
  env: PipelineEnv,
  opts: PipelineOptions
): Promise<PipelineResult> {
  const errors: string[] = [];

  await seedSourcesIfEmpty(env.DB);
  const sources = await getEnabledSources(env.DB);
  if (sources.length === 0) {
    return {
      date: opts.date,
      status: "no-candidates",
      fetchSummaries: [],
      candidateCount: 0,
      shortlistCount: 0,
      shortlist: [],
      errors: ["no enabled sources"],
    };
  }

  const { items, summaries } = await fetchAllSources(sources);

  // Persist source fetch outcomes (best-effort; not fatal if it fails).
  await Promise.all(
    summaries.map((s) =>
      recordSourceFetch(
        env.DB,
        s.sourceId,
        s.ok ? "ok" : "error",
        s.error ?? null
      ).catch((e) => errors.push(`source-status[${s.sourceId}]: ${(e as Error).message}`))
    )
  );

  if (items.length === 0) {
    return {
      date: opts.date,
      status: "no-candidates",
      fetchSummaries: summaries,
      candidateCount: 0,
      shortlistCount: 0,
      shortlist: [],
      errors,
    };
  }

  const scored = scoreItems(items);
  const shortlist = await dedupeAndShortlist(
    env.DB,
    scored,
    opts.shortlistSize ?? DEFAULT_SHORTLIST
  );

  if (shortlist.length === 0) {
    return {
      date: opts.date,
      status: "no-candidates",
      fetchSummaries: summaries,
      candidateCount: items.length,
      shortlistCount: 0,
      shortlist: [],
      errors: [...errors, "all candidates were already seen — nothing fresh"],
    };
  }

  if (opts.dryRun) {
    return {
      date: opts.date,
      status: "dry-run",
      fetchSummaries: summaries,
      candidateCount: items.length,
      shortlistCount: shortlist.length,
      shortlist,
      errors,
    };
  }

  if (!env.ANTHROPIC_API_KEY) {
    throw new Error("ANTHROPIC_API_KEY is not configured");
  }

  const drafted = await draftDaily({
    apiKey: env.ANTHROPIC_API_KEY,
    model: env.ANTHROPIC_MODEL,
    date: opts.date,
    shortlist,
  });

  if (!opts.skipPersist) {
    const persistErr = await persistDraft(env.DB, drafted.daily, {
      candidateCount: items.length,
      shortlistCount: shortlist.length,
      generator: drafted.generator,
      model: drafted.model,
    });
    if (persistErr) errors.push(persistErr);

    // Only mark items "seen" once we successfully drafted with them. This
    // way a transient LLM failure doesn't burn the candidates for tomorrow.
    try {
      await recordSeen(env.DB, shortlist, opts.date);
    } catch (e) {
      errors.push(`record-seen: ${(e as Error).message}`);
    }
  }

  return {
    date: opts.date,
    status: "drafted",
    fetchSummaries: summaries,
    candidateCount: items.length,
    shortlistCount: shortlist.length,
    shortlist,
    daily: drafted.daily,
    model: drafted.model,
    generator: drafted.generator,
    rawResponse: drafted.rawResponse,
    errors,
  };
}

async function persistDraft(
  db: D1Database,
  daily: Daily,
  meta: {
    candidateCount: number;
    shortlistCount: number;
    generator: string;
    model: string;
  }
): Promise<string | null> {
  try {
    await db
      .prepare(
        `INSERT INTO daily_drafts
         (date, status, payload, candidate_count, shortlist_count,
          generator, generator_model, generated_at)
         VALUES (?, 'draft', ?, ?, ?, ?, ?, ?)
         ON CONFLICT(date) DO UPDATE SET
           status = 'draft',
           payload = excluded.payload,
           candidate_count = excluded.candidate_count,
           shortlist_count = excluded.shortlist_count,
           generator = excluded.generator,
           generator_model = excluded.generator_model,
           generated_at = excluded.generated_at`
      )
      .bind(
        daily.date,
        JSON.stringify(daily),
        meta.candidateCount,
        meta.shortlistCount,
        meta.generator,
        meta.model,
        now()
      )
      .run();
    return null;
  } catch (e) {
    return `persist-draft: ${(e as Error).message}`;
  }
}

export interface DraftRow {
  date: string;
  status: string;
  payload: string;
  candidate_count: number;
  shortlist_count: number;
  generator: string;
  generator_model: string | null;
  generated_at: number;
  reviewed_at: number | null;
  notes: string | null;
}

export async function getDraft(
  db: D1Database,
  date: string
): Promise<DraftRow | null> {
  const row = await db
    .prepare(
      `SELECT date, status, payload, candidate_count, shortlist_count,
              generator, generator_model, generated_at, reviewed_at, notes
       FROM daily_drafts WHERE date = ?`
    )
    .bind(date)
    .first<DraftRow>();
  return row ?? null;
}

export async function listDrafts(
  db: D1Database,
  limit = 30
): Promise<DraftRow[]> {
  const res = await db
    .prepare(
      `SELECT date, status, payload, candidate_count, shortlist_count,
              generator, generator_model, generated_at, reviewed_at, notes
       FROM daily_drafts ORDER BY date DESC LIMIT ?`
    )
    .bind(limit)
    .all<DraftRow>();
  return res.results;
}

export async function setDraftStatus(
  db: D1Database,
  date: string,
  status: "draft" | "reviewed" | "published" | "discarded",
  notes?: string
): Promise<boolean> {
  const res = await db
    .prepare(
      `UPDATE daily_drafts
       SET status = ?, reviewed_at = ?, notes = COALESCE(?, notes)
       WHERE date = ?`
    )
    .bind(status, now(), notes ?? null, date)
    .run();
  return res.meta.changes > 0;
}

export function todayInIST(): string {
  // Return YYYY-MM-DD for the current calendar day in Asia/Kolkata.
  const d = new Date();
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  // en-CA returns YYYY-MM-DD already
  return fmt.format(d);
}
