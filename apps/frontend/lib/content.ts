import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { fetchTools, fetchNews, ApiTool, ApiNews } from "./api";

// Types
export interface ToolFrontmatter {
  name: string;
  slug: string;
  description: string;
  url: string;
  logoUrl?: string;
  vertical: "agtech" | "legal" | "devtools" | "marketing" | "general";
  categories: string[];
  tags: string[];
  trustScore: number;
  wrapperStatus: "native" | "fine_tuned" | "rag" | "wrapper" | "unknown";
  isVerified: boolean;
  pricing: {
    type: "free" | "freemium" | "paid" | "enterprise";
    startingPrice?: number;
    currency?: string;
    billingPeriod?: "monthly" | "yearly" | "one-time";
  };
  lastAuditedAt?: string;
  createdAt: string;
}

export interface Tool extends ToolFrontmatter {
  content: string;
}

export interface NewsFrontmatter {
  title: string;
  slug: string;
  excerpt: string;
  author: string;
  publishedAt: string;
  vertical?: string;
  tags: string[];
  hypeScore?: number;
  coverImage?: string;
  status: "draft" | "published" | "archived";
}

export interface NewsArticle extends NewsFrontmatter {
  content: string;
}

// Convert API types to local types
function apiToolToTool(apiTool: ApiTool): Tool {
  return {
    name: apiTool.name,
    slug: apiTool.slug,
    description: apiTool.description,
    url: apiTool.url,
    logoUrl: apiTool.logoUrl,
    vertical: apiTool.vertical as Tool["vertical"],
    categories: apiTool.categories,
    tags: apiTool.tags,
    trustScore: apiTool.trustScore,
    wrapperStatus: apiTool.wrapperStatus as Tool["wrapperStatus"],
    isVerified: apiTool.isVerified,
    pricing: {
      type: apiTool.pricing.type as Tool["pricing"]["type"],
      startingPrice: apiTool.pricing.startingPrice,
      currency: apiTool.pricing.currency,
      billingPeriod: apiTool.pricing.billingPeriod as Tool["pricing"]["billingPeriod"],
    },
    lastAuditedAt: apiTool.lastAuditedAt,
    createdAt: apiTool.createdAt,
    content: apiTool.content || "",
  };
}

function apiNewsToNews(apiNews: ApiNews): NewsArticle {
  return {
    title: apiNews.title,
    slug: apiNews.slug,
    excerpt: apiNews.excerpt,
    author: apiNews.author,
    publishedAt: apiNews.publishedAt,
    vertical: apiNews.vertical,
    tags: apiNews.tags,
    hypeScore: apiNews.hypeScore,
    coverImage: apiNews.coverImage,
    status: apiNews.status as NewsArticle["status"],
    content: apiNews.content || "",
  };
}

// Paths
const CONTENT_DIR = path.join(process.cwd(), "content");
const TOOLS_DIR = path.join(CONTENT_DIR, "tools");
const NEWS_DIR = path.join(CONTENT_DIR, "news");

// Ensure directories exist
function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// Get all MDX files from a directory
function getMDXFiles(dir: string): string[] {
  ensureDir(dir);
  try {
    return fs.readdirSync(dir).filter((file) => file.endsWith(".mdx"));
  } catch {
    return [];
  }
}

// Parse MDX file
function parseMDXFile<T>(filePath: string): { frontmatter: T; content: string } {
  const fileContent = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(fileContent);
  return { frontmatter: data as T, content };
}

// Tools - Static file reader (fallback)
function getStaticTools(): Tool[] {
  const files = getMDXFiles(TOOLS_DIR);
  return files
    .map((file) => {
      const { frontmatter, content } = parseMDXFile<ToolFrontmatter>(
        path.join(TOOLS_DIR, file)
      );
      return { ...frontmatter, content };
    })
    .sort((a, b) => b.trustScore - a.trustScore);
}

// Tools - Hybrid (API with fallback)
export function getAllTools(): Tool[] {
  // For static generation, use MDX files
  // API data is fetched at runtime via fetchTools()
  return getStaticTools();
}

// Async version that tries API first
export async function getAllToolsAsync(): Promise<Tool[]> {
  try {
    const response = await fetchTools();
    if (response.data && response.data.tools.length > 0) {
      return response.data.tools.map(apiToolToTool);
    }
  } catch (error) {
    console.warn("API unavailable, falling back to static files:", error);
  }
  return getStaticTools();
}

export function getToolBySlug(slug: string): Tool | null {
  const filePath = path.join(TOOLS_DIR, `${slug}.mdx`);
  if (!fs.existsSync(filePath)) return null;
  const { frontmatter, content } = parseMDXFile<ToolFrontmatter>(filePath);
  return { ...frontmatter, content };
}

export function getToolsByVertical(vertical: string): Tool[] {
  return getAllTools().filter((tool) => tool.vertical === vertical);
}

export function getToolsByCategory(category: string): Tool[] {
  return getAllTools().filter((tool) => tool.categories.includes(category));
}

export function getFeaturedTools(limit = 6): Tool[] {
  return getAllTools()
    .filter((tool) => tool.isVerified && tool.trustScore >= 80)
    .slice(0, limit);
}

// News - Static file reader (fallback)
function getStaticNews(): NewsArticle[] {
  const files = getMDXFiles(NEWS_DIR);
  return files
    .map((file) => {
      const { frontmatter, content } = parseMDXFile<NewsFrontmatter>(
        path.join(NEWS_DIR, file)
      );
      return { ...frontmatter, content };
    })
    .filter((article) => article.status === "published")
    .sort(
      (a, b) =>
        new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
    );
}

// News - Hybrid (API with fallback)
export function getAllNews(): NewsArticle[] {
  // For static generation, use MDX files
  // API data is fetched at runtime via fetchNews()
  return getStaticNews();
}

// Async version that tries API first
export async function getAllNewsAsync(): Promise<NewsArticle[]> {
  try {
    const response = await fetchNews();
    if (response.data && response.data.news.length > 0) {
      return response.data.news.map(apiNewsToNews);
    }
  } catch (error) {
    console.warn("API unavailable, falling back to static files:", error);
  }
  return getStaticNews();
}

export function getNewsBySlug(slug: string): NewsArticle | null {
  const filePath = path.join(NEWS_DIR, `${slug}.mdx`);
  if (!fs.existsSync(filePath)) return null;
  const { frontmatter, content } = parseMDXFile<NewsFrontmatter>(filePath);
  return { ...frontmatter, content };
}

export function getNewsByVertical(vertical: string): NewsArticle[] {
  return getAllNews().filter((article) => article.vertical === vertical);
}

export function getRecentNews(limit = 5): NewsArticle[] {
  return getAllNews().slice(0, limit);
}

// Categories & Verticals
export function getAllCategories(): string[] {
  const tools = getAllTools();
  const categories = new Set<string>();
  tools.forEach((tool) => {
    tool.categories.forEach((cat) => categories.add(cat));
  });
  return Array.from(categories).sort();
}

export function getAllVerticals(): string[] {
  return ["agtech", "legal", "devtools", "marketing", "general"];
}

// Search utilities
export function searchTools(query: string): Tool[] {
  const q = query.toLowerCase();
  return getAllTools().filter(
    (tool) =>
      tool.name.toLowerCase().includes(q) ||
      tool.description.toLowerCase().includes(q) ||
      tool.tags.some((tag) => tag.toLowerCase().includes(q)) ||
      tool.categories.some((cat) => cat.toLowerCase().includes(q))
  );
}

// Stats
export function getToolStats() {
  const tools = getAllTools();
  return {
    total: tools.length,
    verified: tools.filter((t) => t.isVerified).length,
    wrappers: tools.filter((t) => t.wrapperStatus === "wrapper").length,
    avgTrustScore: Math.round(
      tools.reduce((sum, t) => sum + t.trustScore, 0) / tools.length
    ),
    byVertical: getAllVerticals().reduce(
      (acc, v) => {
        acc[v] = tools.filter((t) => t.vertical === v).length;
        return acc;
      },
      {} as Record<string, number>
    ),
  };
}

