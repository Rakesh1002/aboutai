import { now } from "@/lib/cf";
import type { FetchedItem } from "./fetch";
import { urlHash } from "./fetch";

export interface ScoredItem extends FetchedItem {
  score: number;
  urlHash: string;
}

// Two-axis scorer: (1) intrinsic India-builder relevance from keywords +
// source weight, (2) recency decay. Final score is multiplicative so a
// week-old global item can still beat a 12-hour ad-tech post if the
// keyword density says so. The LLM is the final arbiter — this scorer's
// only job is to keep the prompt under context limits.

const STRONG_INDIA_TOKENS = [
  "india", "indian", "bengaluru", "bangalore", "mumbai", "delhi",
  "hyderabad", "chennai", "pune", "noida", "gurgaon", "gurugram",
  "meity", "rbi", "sebi", "trai", "ondc", "upi", "aadhaar", "digi",
  "iit", "iisc", "iim", "yourstory", "inc42", "ettech",
  "sarvam", "krutrim", "ola krutrim", "yotta", "infosys", "tcs", "wipro",
  "razorpay", "zoho", "freshworks", "swiggy", "zomato", "paytm",
];

const STRONG_BUILDER_TOKENS = [
  "api", "sdk", "model", "llm", "gpt", "claude", "gemini", "mistral",
  "llama", "qwen", "deepseek", "anthropic", "openai", "huggingface",
  "agent", "agents", "rag", "embedding", "vector", "fine-tun",
  "inference", "tokens", "context window", "tool use", "structured output",
  "prompt cach", "throughput", "latency", "pricing", "cents per",
  "dollars per", "cost per", "open source", "open-weight", "weights",
  "release", "ga", "beta", "preview", "deprecat", "voice", "realtime",
  "evals", "benchmark", "mcp", "tool calling",
];

const NOISE_TOKENS = [
  "horoscope", "celebrity", "bollywood", "cricket", "share price target",
  "weather", "election results", "stock recommendation",
];

function tokens(input: string): string {
  return input.toLowerCase();
}

function keywordHits(text: string, list: readonly string[]): number {
  let n = 0;
  for (const k of list) if (text.includes(k)) n += 1;
  return n;
}

function recencyMultiplier(publishedAt: number, nowSec: number): number {
  if (!publishedAt) return 0.5; // unknown date — light penalty
  const ageHours = Math.max(0, (nowSec - publishedAt) / 3600);
  if (ageHours <= 24) return 1.0;
  if (ageHours <= 48) return 0.85;
  if (ageHours <= 72) return 0.65;
  if (ageHours <= 168) return 0.4;
  return 0.15;
}

export function scoreItems(items: readonly FetchedItem[]): FetchedItem[] {
  const t = now();
  const scored = items.map((item) => {
    const text = tokens(item.title + " " + item.summary);
    const indiaHits = keywordHits(text, STRONG_INDIA_TOKENS);
    const builderHits = keywordHits(text, STRONG_BUILDER_TOKENS);
    const noiseHits = keywordHits(text, NOISE_TOKENS);

    const regionBoost = item.sourceRegion === "india" ? 1.2 : 1.0;
    const indiaSignal = 1 + indiaHits * 0.6;
    const builderSignal = 1 + builderHits * 0.35;
    const noisePenalty = Math.pow(0.4, noiseHits);

    const intrinsic =
      item.sourceWeight * regionBoost * indiaSignal * builderSignal * noisePenalty;
    const score = intrinsic * recencyMultiplier(item.publishedAt, t);

    return { ...item, score };
  });

  return scored.sort((a, b) => (b as ScoredItem).score - (a as ScoredItem).score);
}

export async function dedupeAndShortlist(
  db: D1Database,
  scored: readonly FetchedItem[],
  shortlistSize: number
): Promise<ScoredItem[]> {
  // Hash all URLs in a single async pass.
  const withHashes: ScoredItem[] = await Promise.all(
    scored.map(async (item) => ({
      ...(item as ScoredItem),
      score: (item as ScoredItem).score ?? 0,
      urlHash: await urlHash(item.url),
    }))
  );

  // Pull seen-set in chunks (D1 has SQL placeholder limits ~100).
  const seen = new Set<string>();
  const chunkSize = 80;
  for (let i = 0; i < withHashes.length; i += chunkSize) {
    const chunk = withHashes.slice(i, i + chunkSize);
    if (chunk.length === 0) continue;
    const placeholders = chunk.map(() => "?").join(",");
    const res = await db
      .prepare(
        `SELECT url_hash FROM aggregator_seen WHERE url_hash IN (${placeholders})`
      )
      .bind(...chunk.map((c) => c.urlHash))
      .all<{ url_hash: string }>();
    for (const row of res.results) seen.add(row.url_hash);
  }

  // Filter dedupe + de-dup by canonical URL (some feeds republish).
  const seenInBatch = new Set<string>();
  const fresh = withHashes.filter((c) => {
    if (seen.has(c.urlHash)) return false;
    if (seenInBatch.has(c.urlHash)) return false;
    seenInBatch.add(c.urlHash);
    return true;
  });

  // Keep at most one item per source domain in the shortlist for variety.
  const perSource = new Map<string, number>();
  const PER_SOURCE_CAP = 2;
  const shortlist: ScoredItem[] = [];
  for (const c of fresh) {
    const used = perSource.get(c.sourceId) ?? 0;
    if (used >= PER_SOURCE_CAP) continue;
    perSource.set(c.sourceId, used + 1);
    shortlist.push(c);
    if (shortlist.length >= shortlistSize) break;
  }
  return shortlist;
}

export async function recordSeen(
  db: D1Database,
  items: readonly ScoredItem[],
  usedInDate: string
): Promise<void> {
  if (items.length === 0) return;
  const t = now();
  const stmts = items.map((item) =>
    db
      .prepare(
        `INSERT OR IGNORE INTO aggregator_seen
         (url_hash, url, source_id, first_seen_at, used_in_date)
         VALUES (?, ?, ?, ?, ?)`
      )
      .bind(item.urlHash, item.url, item.sourceId, t, usedInDate)
  );
  await db.batch(stmts);
}
