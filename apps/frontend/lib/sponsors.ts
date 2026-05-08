import sponsorsData from "@/content/sponsors.json";

export type SponsorClass = "house" | "sponsor" | "exchange";

export interface Sponsor {
  id: string;
  klass: SponsorClass;
  advertiser: string;
  headline: string;
  body: string;
  cta: string;
  url: string;
  starts_at: string;
  ends_at: string;
  weight: number;
}

const ALL_SPONSORS = sponsorsData as Sponsor[];

function isLive(s: Sponsor, nowMs: number): boolean {
  return (
    new Date(s.starts_at).getTime() <= nowMs &&
    nowMs <= new Date(s.ends_at).getTime()
  );
}

export function getSponsorById(id: string): Sponsor | null {
  const found = ALL_SPONSORS.find((s) => s.id === id) ?? null;
  if (!found) return null;
  return isLive(found, Date.now()) ? found : null;
}

// House sponsor fallback when a daily references a sponsor whose run has ended,
// or when a daily intentionally has no inline sponsor configured.
export function pickHouseSponsor(saltSeed: number): Sponsor | null {
  const now = Date.now();
  const pool = ALL_SPONSORS.filter(
    (s) => s.klass === "house" && isLive(s, now)
  );
  if (pool.length === 0) return null;
  return pool[saltSeed % pool.length];
}

export function sponsorClickUrl(id: string): string {
  return `/api/ad/${encodeURIComponent(id)}/click`;
}
