/**
 * API Client for aboutai Backend
 * Fetches live content data with fallback to static MDX files
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081/api/v1";

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  isFromCache: boolean;
}

// Types matching backend responses
export interface ApiTool {
  name: string;
  slug: string;
  description: string;
  url: string;
  logoUrl?: string;
  vertical: string;
  categories: string[];
  tags: string[];
  trustScore: number;
  wrapperStatus: string;
  isVerified: boolean;
  pricing: {
    type: string;
    startingPrice?: number;
    currency?: string;
    billingPeriod?: string;
  };
  lastAuditedAt?: string;
  createdAt: string;
  content?: string;
}

export interface ApiNews {
  title: string;
  slug: string;
  excerpt: string;
  author: string;
  publishedAt: string;
  vertical?: string;
  tags: string[];
  hypeScore?: number;
  coverImage?: string;
  status: string;
  content?: string;
}

export interface ApiLaunch {
  source: string;
  title: string;
  url: string;
  description: string;
  votes: number;
  category: string;
}

export interface ContentStats {
  tools: number;
  news: number;
  lastUpdated: string;
}

// Cache for API responses
const cache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 60 * 1000; // 1 minute cache

async function fetchWithCache<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const cacheKey = endpoint;
  const now = Date.now();

  // Check cache
  const cached = cache.get(cacheKey);
  if (cached && now - cached.timestamp < CACHE_TTL) {
    return { data: cached.data as T, error: null, isFromCache: true };
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      // Revalidate every minute for ISR
      next: { revalidate: 60 },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    // Update cache
    cache.set(cacheKey, { data, timestamp: now });

    return { data, error: null, isFromCache: false };
  } catch (error) {
    console.error(`API fetch failed for ${endpoint}:`, error);

    // Return cached data if available, even if stale
    if (cached) {
      return {
        data: cached.data as T,
        error: (error as Error).message,
        isFromCache: true,
      };
    }

    return { data: null, error: (error as Error).message, isFromCache: false };
  }
}

// =============================================
// Content API
// =============================================

export async function fetchTools(options?: {
  vertical?: string;
  category?: string;
  limit?: number;
}): Promise<
  ApiResponse<{ count: number; tools: ApiTool[]; lastUpdated: string }>
> {
  const params = new URLSearchParams();
  if (options?.vertical) params.set("vertical", options.vertical);
  if (options?.category) params.set("category", options.category);
  if (options?.limit) params.set("limit", options.limit.toString());

  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchWithCache(`/content/tools${query}`);
}

export async function fetchNews(options?: {
  vertical?: string;
  limit?: number;
}): Promise<
  ApiResponse<{ count: number; news: ApiNews[]; lastUpdated: string }>
> {
  const params = new URLSearchParams();
  if (options?.vertical) params.set("vertical", options.vertical);
  if (options?.limit) params.set("limit", options.limit.toString());

  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchWithCache(`/content/news${query}`);
}

export async function fetchContentStats(): Promise<ApiResponse<ContentStats>> {
  return fetchWithCache("/content/stats");
}

// =============================================
// Launches & Discovery API
// =============================================

export async function fetchRecentLaunches(
  limit: number = 50
): Promise<ApiResponse<{ count: number; launches: ApiLaunch[] }>> {
  return fetchWithCache(`/tools/launches?limit=${limit}`);
}

// =============================================
// Platform Stats
// =============================================

export async function fetchPlatformStats(): Promise<
  ApiResponse<{
    newsletter_subscribers: number;
    tools_indexed: number;
    tools_pending: number;
    news_articles: number;
    podcasts: number;
    sources_monitored: number;
  }>
> {
  return fetchWithCache("/stats");
}

// =============================================
// Newsletter
// =============================================

export async function subscribeToNewsletter(
  email: string,
  source: string = "website"
): Promise<{ status: string; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/newsletter/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, source }),
    });

    return response.json();
  } catch (error) {
    console.error("Newsletter subscription failed:", error);
    return { status: "error", message: "Failed to subscribe" };
  }
}

// =============================================
// Tool Submission
// =============================================

export async function submitTool(
  url: string,
  submitterEmail?: string,
  notes?: string
): Promise<{
  status: string;
  message: string;
  submission_id?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        submitter_email: submitterEmail,
        notes,
      }),
    });

    return response.json();
  } catch (error) {
    console.error("Tool submission failed:", error);
    return { status: "error", message: "Failed to submit tool" };
  }
}

// =============================================
// Health Check
// =============================================

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      next: { revalidate: 0 },
    });
    return response.ok;
  } catch {
    return false;
  }
}
