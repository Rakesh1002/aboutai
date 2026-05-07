import fs from "fs";
import path from "path";
import matter from "gray-matter";

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

const CONTENT_DIR = path.join(process.cwd(), "content");
const ESSAYS_DIR = path.join(CONTENT_DIR, "essays");
const STACK_FILE = path.join(CONTENT_DIR, "stack.json");

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function getMDXFiles(dir: string): string[] {
  ensureDir(dir);
  try {
    return fs.readdirSync(dir).filter((f) => f.endsWith(".mdx"));
  } catch {
    return [];
  }
}

function parseEssay(filePath: string): Essay {
  const fileContent = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(fileContent);
  return { ...(data as EssayFrontmatter), content };
}

export function getAllEssays(): Essay[] {
  return getMDXFiles(ESSAYS_DIR)
    .map((file) => parseEssay(path.join(ESSAYS_DIR, file)))
    .filter((e) => e.status !== "draft")
    .sort((a, b) => {
      const aDate = a.publishedAt ? new Date(a.publishedAt).getTime() : 0;
      const bDate = b.publishedAt ? new Date(b.publishedAt).getTime() : 0;
      return bDate - aDate;
    });
}

export function getEssayBySlug(slug: string): Essay | null {
  const filePath = path.join(ESSAYS_DIR, `${slug}.mdx`);
  if (!fs.existsSync(filePath)) return null;
  return parseEssay(filePath);
}

export function getEssaySlugs(): string[] {
  return getAllEssays().map((e) => e.slug);
}

export function getStack(): StackStartup[] {
  if (!fs.existsSync(STACK_FILE)) return [];
  const raw = fs.readFileSync(STACK_FILE, "utf-8");
  return JSON.parse(raw) as StackStartup[];
}
