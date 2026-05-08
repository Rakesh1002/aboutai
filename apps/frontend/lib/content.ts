import stackData from "@/content/stack.json";

export type EssayType =
  | "teardown"
  | "receipts"
  | "stack-snapshot"
  | "vertical"
  | "open-letter"
  | "report";

export type Verdict = "ship-it" | "trial-only" | "avoid";

export type Paywall = "free" | "paid" | "one-time";

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

export function getStack(): StackStartup[] {
  return stackData as StackStartup[];
}
