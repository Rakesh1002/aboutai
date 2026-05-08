import { getCloudflareContext } from "@opennextjs/cloudflare";

export type AppEnv = CloudflareEnv;

export function getEnv(): AppEnv {
  const { env } = getCloudflareContext();
  return env as AppEnv;
}

export function newId(): string {
  return crypto.randomUUID();
}

export function newToken(bytes = 24): string {
  const buf = new Uint8Array(bytes);
  crypto.getRandomValues(buf);
  return Array.from(buf, (b) => b.toString(16).padStart(2, "0")).join("");
}

export function now(): number {
  return Math.floor(Date.now() / 1000);
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function normalizeEmail(input: string): string | null {
  const e = input.trim().toLowerCase();
  if (!EMAIL_RE.test(e)) return null;
  if (e.length > 254) return null;
  return e;
}
