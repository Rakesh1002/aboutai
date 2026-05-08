import stackData from "@/content/stack.json";
import { daily20260512 } from "@/content/daily/2026-05-12";

export type EssayType =
  | "teardown"
  | "receipts"
  | "stack-snapshot"
  | "vertical"
  | "open-letter"
  | "report";

export type Verdict = "ship-it" | "trial-only" | "avoid";

export type Paywall = "free" | "email-gate" | "paid" | "one-time";

export interface EssayFrontmatter {
  title: string;
  slug: string;
  excerpt?: string;
  publishedAt?: string;
  type: EssayType;
  verdict?: Verdict;
  paywall?: Paywall;
  oneTimePriceUsd?: number;
  vendors?: string[];
  tags?: string[];
  status?: "draft" | "published";
}

export interface Essay extends EssayFrontmatter {
  content: string;
}

export type StoryImportance = "must-read" | "notable" | "fyi";

export interface DailyStory {
  headline: string;
  source: string;
  link: string;
  summary: string;
  indiaTakeaway: string;
  importance: StoryImportance;
}

export interface DailySponsorRead {
  sponsorId: string;
}

export interface Daily {
  date: string;
  title: string;
  intro: string;
  outro?: string;
  stories: DailyStory[];
  sponsor?: DailySponsorRead;
  status?: "draft" | "published";
}

export interface StackEntry {
  vendor: string;
  category: string;
  status: "in-production" | "trialing" | "ripped-out";
  startedAt?: string;
  endedAt?: string;
  monthlyCostUsd?: number;
  notes?: string;
}

export interface StackStartup {
  slug: string;
  name: string;
  stage: string;
  url?: string;
  tools: StackEntry[];
}

// Essays are added by importing them explicitly here once a teardown ships.
// This keeps the bundle deterministic and Worker-safe (no runtime fs reads).
// Convention: import the .mdx file as a module, attach the frontmatter we
// want exposed in listings.
const ESSAYS: Essay[] = [];

// Daily Rundowns are TS modules (structured, not prose) — one per weekday Mon–Thu.
// Each new daily ships as a new file under content/daily/YYYY-MM-DD.ts and is
// registered here. The aggregation pipeline writes draft files; humans edit and
// promote status to "published" before this list ships.
const DAILIES: Daily[] = [daily20260512];

export function getAllEssays(): Essay[] {
  return ESSAYS.filter((e) => e.status !== "draft").sort((a, b) => {
    const aDate = a.publishedAt ? new Date(a.publishedAt).getTime() : 0;
    const bDate = b.publishedAt ? new Date(b.publishedAt).getTime() : 0;
    return bDate - aDate;
  });
}

export function getEssayBySlug(slug: string): Essay | null {
  return getAllEssays().find((e) => e.slug === slug) ?? null;
}

export function getEssaySlugs(): string[] {
  return getAllEssays().map((e) => e.slug);
}

export function getAllDailies(): Daily[] {
  return DAILIES.filter((d) => d.status !== "draft").sort((a, b) =>
    b.date.localeCompare(a.date)
  );
}

export function getDailyByDate(date: string): Daily | null {
  return DAILIES.find((d) => d.date === date && d.status !== "draft") ?? null;
}

export function getDailyDates(): string[] {
  return getAllDailies().map((d) => d.date);
}

export function getStack(): StackStartup[] {
  return stackData as StackStartup[];
}
