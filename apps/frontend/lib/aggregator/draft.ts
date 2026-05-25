import type { Daily, DailyStory, StoryImportance } from "@/lib/content";
import type { ScoredItem } from "./score";

export interface DraftResult {
  daily: Daily;
  model: string;
  generator: string;
  rawResponse: string;
}

const DEFAULT_MODEL = "claude-opus-4-7";
const ANTHROPIC_VERSION = "2023-06-01";
const ANTHROPIC_BETA = "prompt-caching-2024-07-31";

const SYSTEM_PROMPT = `You are the lead editor of *The AI Daily*, a weekday brief written for Indian AI builders, founders, PMs, and engineers shipping AI products in India.

Your job: given a shortlist of candidate stories scraped from RSS feeds, pick the FIVE most important for this audience and produce structured story cards.

Editorial rules:
- Audience is Indian AI builders. Global news is included only if it changes what an Indian builder should do this week (pricing, new model capabilities, regional latency, regulation, capital flow, infra availability).
- Voice: tight, technical, no hype, no marketing words, no exclamation marks, no emojis. Write like a senior engineer briefing other senior engineers over coffee.
- Each story has an "indiaTakeaway" — a one-or-two sentence concrete consequence for an Indian builder. NOT a summary. NOT a quote. Always a "do this", "watch for that", or "this changes the math because".
- "summary" is a 1–2 sentence factual recap of the news. Do NOT speculate. Do NOT add facts not in the source title or description.
- "importance" is one of: "must-read", "notable", "fyi". Cap "must-read" at 2 per day. The order in the output is the order they appear in the email.
- If a candidate is hype, vendor PR with no substance, recycled news, or irrelevant to Indian builders — drop it. Better to ship 4 strong stories than 5 with one weak.
- Headlines: rewrite the source headline if needed for clarity, but never invent facts. Keep headlines ≤120 chars.

Output: a single JSON object exactly matching this TypeScript type, with NO surrounding prose or markdown:

{
  "intro": string,           // 2–3 sentences, sets the day's frame
  "outro": string | null,    // optional 1 sentence sign-off
  "stories": Array<{
    "headline": string,
    "source": string,        // publication name from the candidate
    "link": string,          // canonical URL from the candidate
    "summary": string,
    "indiaTakeaway": string,
    "importance": "must-read" | "notable" | "fyi"
  }>
}`;

function buildUserPrompt(date: string, shortlist: readonly ScoredItem[]): string {
  const lines = [
    `Date: ${date} (Asia/Kolkata)`,
    `Candidates (${shortlist.length}, ranked by relevance score):`,
    "",
  ];
  shortlist.forEach((item, i) => {
    lines.push(`[${i + 1}] ${item.title}`);
    lines.push(`    source: ${item.sourceName} (${item.sourceRegion}, weight ${item.sourceWeight.toFixed(1)})`);
    lines.push(`    url: ${item.url}`);
    if (item.publishedAt) {
      lines.push(`    published: ${new Date(item.publishedAt * 1000).toISOString()}`);
    }
    if (item.summary) {
      lines.push(`    summary: ${item.summary.slice(0, 600)}`);
    }
    lines.push("");
  });
  lines.push(
    "Pick the top stories. Reply with the JSON object only — no markdown fence, no commentary."
  );
  return lines.join("\n");
}

interface AnthropicResponse {
  content?: Array<{ type: string; text?: string }>;
  model?: string;
  error?: { type: string; message: string };
}

interface ParsedDraft {
  intro: string;
  outro?: string | null;
  stories: DailyStory[];
}

function extractJson(s: string): string {
  // The system prompt asks for raw JSON, but tolerate a stray fence.
  const fence = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) return fence[1].trim();
  const first = s.indexOf("{");
  const last = s.lastIndexOf("}");
  if (first >= 0 && last > first) return s.slice(first, last + 1);
  return s.trim();
}

const ALLOWED_IMPORTANCE: ReadonlySet<StoryImportance> = new Set([
  "must-read",
  "notable",
  "fyi",
]);

function validateDraft(parsed: unknown): ParsedDraft {
  if (!parsed || typeof parsed !== "object") {
    throw new Error("draft is not an object");
  }
  const p = parsed as Record<string, unknown>;
  if (typeof p.intro !== "string" || p.intro.length < 10) {
    throw new Error("draft.intro missing or too short");
  }
  if (!Array.isArray(p.stories) || p.stories.length === 0) {
    throw new Error("draft.stories empty");
  }
  const stories: DailyStory[] = p.stories.map((raw, i) => {
    if (!raw || typeof raw !== "object") {
      throw new Error(`stories[${i}] is not an object`);
    }
    const s = raw as Record<string, unknown>;
    const importance = s.importance as StoryImportance;
    if (typeof s.headline !== "string" || !s.headline) {
      throw new Error(`stories[${i}].headline missing`);
    }
    if (typeof s.source !== "string" || !s.source) {
      throw new Error(`stories[${i}].source missing`);
    }
    if (typeof s.link !== "string" || !/^https?:\/\//.test(s.link)) {
      throw new Error(`stories[${i}].link missing or invalid`);
    }
    if (typeof s.summary !== "string" || s.summary.length < 10) {
      throw new Error(`stories[${i}].summary missing or too short`);
    }
    if (typeof s.indiaTakeaway !== "string" || s.indiaTakeaway.length < 10) {
      throw new Error(`stories[${i}].indiaTakeaway missing or too short`);
    }
    if (!ALLOWED_IMPORTANCE.has(importance)) {
      throw new Error(`stories[${i}].importance invalid: ${String(importance)}`);
    }
    return {
      headline: s.headline,
      source: s.source,
      link: s.link,
      summary: s.summary,
      indiaTakeaway: s.indiaTakeaway,
      importance,
    };
  });

  return {
    intro: p.intro,
    outro: typeof p.outro === "string" ? p.outro : undefined,
    stories,
  };
}

function dailyTitleFor(date: string): string {
  const d = new Date(date + "T00:00:00+05:30");
  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Kolkata",
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
  // "Tue, May 12, 2026"
  return `Daily — ${fmt.format(d)}`;
}

export interface DraftOptions {
  apiKey: string;
  model?: string;
  date: string;
  shortlist: readonly ScoredItem[];
}

export async function draftDaily(opts: DraftOptions): Promise<DraftResult> {
  const model = opts.model ?? DEFAULT_MODEL;
  const userPrompt = buildUserPrompt(opts.date, opts.shortlist);

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": opts.apiKey,
      "anthropic-version": ANTHROPIC_VERSION,
      "anthropic-beta": ANTHROPIC_BETA,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model,
      max_tokens: 4096,
      temperature: 0.4,
      system: [
        {
          type: "text",
          text: SYSTEM_PROMPT,
          cache_control: { type: "ephemeral" },
        },
      ],
      messages: [
        { role: "user", content: [{ type: "text", text: userPrompt }] },
      ],
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`anthropic ${res.status}: ${text.slice(0, 500)}`);
  }

  const body = (await res.json()) as AnthropicResponse;
  if (body.error) {
    throw new Error(`anthropic error: ${body.error.type} — ${body.error.message}`);
  }
  const text = body.content?.find((c) => c.type === "text")?.text ?? "";
  if (!text) throw new Error("anthropic returned no text content");

  const jsonStr = extractJson(text);
  let parsed: unknown;
  try {
    parsed = JSON.parse(jsonStr);
  } catch (e) {
    throw new Error(`draft JSON parse failed: ${(e as Error).message}\n--\n${jsonStr.slice(0, 600)}`);
  }
  const draft = validateDraft(parsed);

  const daily: Daily = {
    date: opts.date,
    title: dailyTitleFor(opts.date),
    intro: draft.intro,
    outro: draft.outro ?? undefined,
    status: "draft",
    stories: draft.stories,
  };

  return {
    daily,
    model: body.model ?? model,
    generator: "anthropic-messages-v1",
    rawResponse: text,
  };
}
