import type { SourceRow } from "./sources";

export interface FetchedItem {
  sourceId: string;
  sourceName: string;
  sourceRegion: "india" | "global";
  sourceWeight: number;
  url: string;
  title: string;
  summary: string;
  publishedAt: number;
}

export interface FetchSummary {
  sourceId: string;
  ok: boolean;
  count: number;
  error?: string;
}

const FEED_TIMEOUT_MS = 8000;
const UA = "TheAIDailyAggregator/1.0 (+https://theaidaily.in)";

// Tags can be like <title>x</title> or <title><![CDATA[x]]></title> and may
// carry attributes. The parser is regex-based on purpose: workerd has no
// DOMParser, and pulling in fast-xml-parser doubles the bundle. Feeds we
// don't recognize get logged and skipped — better than corrupt drafts.
function decodeEntities(s: string): string {
  return s
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) =>
      String.fromCodePoint(parseInt(h, 16))
    )
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&nbsp;/g, " ");
}

function stripTags(s: string): string {
  return decodeEntities(s)
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function pickInner(raw: string, tag: string): string | null {
  const re = new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i");
  const m = raw.match(re);
  if (!m) return null;
  return decodeEntities(m[1]).trim();
}

function pickAttr(raw: string, tag: string, attr: string): string | null {
  const re = new RegExp(`<${tag}\\b[^>]*\\b${attr}=["']([^"']+)["']`, "i");
  const m = raw.match(re);
  return m ? decodeEntities(m[1]).trim() : null;
}

function parsePubDate(s: string | null): number {
  if (!s) return 0;
  const t = Date.parse(s);
  if (Number.isNaN(t)) return 0;
  return Math.floor(t / 1000);
}

function isLikelyAtom(xml: string): boolean {
  return /<feed\b[^>]*xmlns=["']http:\/\/www\.w3\.org\/2005\/Atom/i.test(xml);
}

function splitItems(xml: string, tag: "item" | "entry"): string[] {
  const re = new RegExp(`<${tag}\\b[^>]*>[\\s\\S]*?<\\/${tag}>`, "gi");
  return xml.match(re) ?? [];
}

function pickRssLink(raw: string): string | null {
  // RSS: <link>https://...</link>; some feeds use <link/> attr in atom-ish.
  const inner = pickInner(raw, "link");
  if (inner && /^https?:\/\//i.test(inner)) return inner;
  const href = pickAttr(raw, "link", "href");
  return href;
}

function pickAtomLink(raw: string): string | null {
  // Prefer rel="alternate" link, fall back to first <link href>.
  const altMatch = raw.match(
    /<link\b[^>]*\brel=["']alternate["'][^>]*\bhref=["']([^"']+)["']/i
  );
  if (altMatch) return decodeEntities(altMatch[1]);
  return pickAttr(raw, "link", "href");
}

interface ParseContext {
  source: SourceRow;
}

function parseRss(xml: string, ctx: ParseContext): FetchedItem[] {
  return splitItems(xml, "item")
    .map<FetchedItem | null>((raw) => {
      const url = pickRssLink(raw) ?? pickInner(raw, "guid");
      const title = pickInner(raw, "title");
      if (!url || !title) return null;
      const summary =
        stripTags(pickInner(raw, "description") ?? "") ||
        stripTags(pickInner(raw, "content:encoded") ?? "");
      const publishedAt = parsePubDate(
        pickInner(raw, "pubDate") ?? pickInner(raw, "dc:date")
      );
      return {
        sourceId: ctx.source.id,
        sourceName: ctx.source.name,
        sourceRegion: ctx.source.region,
        sourceWeight: ctx.source.weight,
        url: url.split("#")[0],
        title: stripTags(title),
        summary: summary.slice(0, 1200),
        publishedAt,
      };
    })
    .filter((x): x is FetchedItem => x !== null);
}

function parseAtom(xml: string, ctx: ParseContext): FetchedItem[] {
  return splitItems(xml, "entry")
    .map<FetchedItem | null>((raw) => {
      const url = pickAtomLink(raw);
      const title = pickInner(raw, "title");
      if (!url || !title) return null;
      const summary =
        stripTags(pickInner(raw, "summary") ?? "") ||
        stripTags(pickInner(raw, "content") ?? "");
      const publishedAt = parsePubDate(
        pickInner(raw, "published") ?? pickInner(raw, "updated")
      );
      return {
        sourceId: ctx.source.id,
        sourceName: ctx.source.name,
        sourceRegion: ctx.source.region,
        sourceWeight: ctx.source.weight,
        url: url.split("#")[0],
        title: stripTags(title),
        summary: summary.slice(0, 1200),
        publishedAt,
      };
    })
    .filter((x): x is FetchedItem => x !== null);
}

async function fetchOne(source: SourceRow): Promise<{
  items: FetchedItem[];
  error?: string;
}> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), FEED_TIMEOUT_MS);
  try {
    const res = await fetch(source.url, {
      headers: { "user-agent": UA, accept: "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5" },
      signal: ctrl.signal,
      cf: { cacheTtl: 600, cacheEverything: true } as RequestInitCfProperties,
    });
    if (!res.ok) {
      return { items: [], error: `http ${res.status}` };
    }
    const xml = await res.text();
    const ctx: ParseContext = { source };
    const useAtom = source.kind === "atom" || isLikelyAtom(xml);
    const items = useAtom ? parseAtom(xml, ctx) : parseRss(xml, ctx);
    return { items };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "unknown";
    return { items: [], error: msg };
  } finally {
    clearTimeout(timer);
  }
}

export async function fetchAllSources(
  sources: readonly SourceRow[]
): Promise<{ items: FetchedItem[]; summaries: FetchSummary[] }> {
  const results = await Promise.all(
    sources.map(async (s) => {
      const r = await fetchOne(s);
      const summary: FetchSummary = {
        sourceId: s.id,
        ok: !r.error,
        count: r.items.length,
        error: r.error,
      };
      return { items: r.items, summary };
    })
  );
  const items = results.flatMap((r) => r.items);
  const summaries = results.map((r) => r.summary);
  return { items, summaries };
}

export async function urlHash(url: string): Promise<string> {
  const data = new TextEncoder().encode(url.toLowerCase());
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
