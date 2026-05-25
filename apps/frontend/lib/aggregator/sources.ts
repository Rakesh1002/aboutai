import { newId, now } from "@/lib/cf";

export type SourceRegion = "india" | "global";
export type SourceKind = "rss" | "atom";

export interface SourceSeed {
  id: string;
  name: string;
  url: string;
  kind: SourceKind;
  region: SourceRegion;
  weight: number;
}

// India-flavored AI-builder source set. India region carries heavier weight
// in the scorer because the publication is for Indian builders. Global
// sources are filtered down in the LLM draft step — only what matters to an
// Indian builder this week makes the cut.
//
// IDs are stable so the seeder can upsert idempotently.
export const SEED_SOURCES: readonly SourceSeed[] = [
  // India ecosystem + builder press
  { id: "src-inc42", name: "Inc42", url: "https://inc42.com/feed/", kind: "rss", region: "india", weight: 1.6 },
  { id: "src-yourstory", name: "YourStory", url: "https://yourstory.com/feed", kind: "rss", region: "india", weight: 1.4 },
  { id: "src-ettech", name: "ETtech", url: "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms", kind: "rss", region: "india", weight: 1.3 },
  { id: "src-aim", name: "Analytics India Magazine", url: "https://analyticsindiamag.com/feed/", kind: "rss", region: "india", weight: 1.5 },
  { id: "src-the-ken-tech", name: "The Ken — Tech", url: "https://the-ken.com/feed/", kind: "rss", region: "india", weight: 1.1 },
  { id: "src-moneycontrol-tech", name: "Moneycontrol — Tech", url: "https://www.moneycontrol.com/rss/technology.xml", kind: "rss", region: "india", weight: 0.9 },

  // Frontier-lab announcements
  { id: "src-anthropic", name: "Anthropic News", url: "https://www.anthropic.com/news/rss.xml", kind: "rss", region: "global", weight: 1.6 },
  { id: "src-openai", name: "OpenAI Blog", url: "https://openai.com/blog/rss.xml", kind: "rss", region: "global", weight: 1.5 },
  { id: "src-googledeepmind", name: "Google DeepMind", url: "https://deepmind.google/blog/rss.xml", kind: "rss", region: "global", weight: 1.3 },
  { id: "src-meta-ai", name: "Meta AI", url: "https://ai.meta.com/blog/rss/", kind: "rss", region: "global", weight: 1.1 },
  { id: "src-mistral", name: "Mistral AI", url: "https://mistral.ai/news/rss.xml", kind: "rss", region: "global", weight: 1.0 },
  { id: "src-huggingface", name: "Hugging Face Blog", url: "https://huggingface.co/blog/feed.xml", kind: "atom", region: "global", weight: 1.0 },

  // Builder infra (Indian-builder-relevant)
  { id: "src-cloudflare-blog", name: "Cloudflare Blog", url: "https://blog.cloudflare.com/rss/", kind: "rss", region: "global", weight: 1.2 },
  { id: "src-vercel-blog", name: "Vercel Blog", url: "https://vercel.com/atom", kind: "atom", region: "global", weight: 0.9 },

  // Tech press — heavy filtering, only India-relevant items
  { id: "src-tc-ai", name: "TechCrunch — AI", url: "https://techcrunch.com/category/artificial-intelligence/feed/", kind: "rss", region: "global", weight: 0.8 },
  { id: "src-verge-ai", name: "The Verge — AI", url: "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", kind: "atom", region: "global", weight: 0.7 },
  { id: "src-mit-tr-ai", name: "MIT Tech Review — AI", url: "https://www.technologyreview.com/topic/artificial-intelligence/feed/", kind: "rss", region: "global", weight: 0.8 },

  // Discussion + research firehose
  { id: "src-hn-ai", name: "Hacker News — AI front page", url: "https://hnrss.org/frontpage?q=AI+OR+LLM&count=30", kind: "rss", region: "global", weight: 0.6 },
];

export interface SourceRow {
  id: string;
  name: string;
  url: string;
  kind: SourceKind;
  region: SourceRegion;
  weight: number;
  enabled: number;
  last_fetched_at: number | null;
  last_status: string | null;
  last_error: string | null;
  created_at: number;
}

export async function seedSourcesIfEmpty(db: D1Database): Promise<number> {
  const existing = await db
    .prepare("SELECT COUNT(*) as n FROM aggregator_sources")
    .first<{ n: number }>();
  if ((existing?.n ?? 0) > 0) return 0;

  const created = now();
  const stmts = SEED_SOURCES.map((s) =>
    db
      .prepare(
        `INSERT INTO aggregator_sources
         (id, name, url, kind, region, weight, enabled, created_at)
         VALUES (?, ?, ?, ?, ?, ?, 1, ?)`
      )
      .bind(s.id, s.name, s.url, s.kind, s.region, s.weight, created)
  );
  await db.batch(stmts);
  return SEED_SOURCES.length;
}

export async function getEnabledSources(db: D1Database): Promise<SourceRow[]> {
  const res = await db
    .prepare(
      `SELECT id, name, url, kind, region, weight, enabled,
              last_fetched_at, last_status, last_error, created_at
       FROM aggregator_sources WHERE enabled = 1 ORDER BY weight DESC, name ASC`
    )
    .all<SourceRow>();
  return res.results;
}

export async function recordSourceFetch(
  db: D1Database,
  sourceId: string,
  status: "ok" | "error",
  error: string | null
): Promise<void> {
  await db
    .prepare(
      `UPDATE aggregator_sources
       SET last_fetched_at = ?, last_status = ?, last_error = ?
       WHERE id = ?`
    )
    .bind(now(), status, error, sourceId)
    .run();
}

export async function addSource(
  db: D1Database,
  input: Omit<SourceSeed, "id"> & { id?: string }
): Promise<string> {
  const id = input.id ?? `src-${newId().slice(0, 8)}`;
  await db
    .prepare(
      `INSERT INTO aggregator_sources
       (id, name, url, kind, region, weight, enabled, created_at)
       VALUES (?, ?, ?, ?, ?, ?, 1, ?)`
    )
    .bind(id, input.name, input.url, input.kind, input.region, input.weight, now())
    .run();
  return id;
}

export async function setSourceEnabled(
  db: D1Database,
  id: string,
  enabled: boolean
): Promise<void> {
  await db
    .prepare("UPDATE aggregator_sources SET enabled = ? WHERE id = ?")
    .bind(enabled ? 1 : 0, id)
    .run();
}
