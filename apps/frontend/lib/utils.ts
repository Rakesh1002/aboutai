import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date));
}

export function formatRelativeDate(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);

  if (diffInSeconds < 60) return "just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  return formatDate(date);
}

export function getTrustScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-500";
  if (score >= 60) return "text-amber-500";
  return "text-red-500";
}

export function getTrustScoreBg(score: number): string {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-amber-500";
  return "bg-red-500";
}

export function getTrustScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Very Good";
  if (score >= 70) return "Good";
  if (score >= 60) return "Fair";
  if (score >= 50) return "Poor";
  return "Very Poor";
}

export function getWrapperStatusLabel(
  status: "native" | "fine_tuned" | "rag" | "wrapper" | "unknown"
): string {
  const labels = {
    native: "Native AI",
    fine_tuned: "Fine-Tuned",
    rag: "RAG Application",
    wrapper: "UI Wrapper",
    unknown: "Unknown",
  };
  return labels[status];
}

export function getWrapperStatusColor(
  status: "native" | "fine_tuned" | "rag" | "wrapper" | "unknown"
): string {
  const colors = {
    native: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950",
    fine_tuned: "text-blue-600 bg-blue-50 dark:bg-blue-950",
    rag: "text-purple-600 bg-purple-50 dark:bg-purple-950",
    wrapper: "text-amber-600 bg-amber-50 dark:bg-amber-950",
    unknown: "text-zinc-600 bg-zinc-50 dark:bg-zinc-900",
  };
  return colors[status];
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/--+/g, "-")
    .trim();
}

export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length).trim() + "...";
}

export function getBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "http://localhost:3000";
}

export function absoluteUrl(path: string): string {
  return `${getBaseUrl()}${path}`;
}
