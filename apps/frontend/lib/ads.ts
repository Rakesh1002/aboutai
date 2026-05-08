import adsData from "@/content/ads.json";

export type AdSlot = "left" | "right" | "both";
export type AdClass = "house" | "sponsor" | "exchange";

export interface Ad {
  id: string;
  klass: AdClass;
  slot: AdSlot;
  advertiser: string;
  logo: string | null;
  headline: string;
  subhead?: string;
  cta: string;
  url: string;
  starts_at: string;
  ends_at: string;
  weight: number;
}

const ALL_ADS = adsData as Ad[];

function isLive(ad: Ad, nowMs: number): boolean {
  const startMs = new Date(ad.starts_at).getTime();
  const endMs = new Date(ad.ends_at).getTime();
  return startMs <= nowMs && nowMs <= endMs;
}

function fitsSlot(ad: Ad, slot: "left" | "right"): boolean {
  return ad.slot === slot || ad.slot === "both";
}

function weightedPick(pool: Ad[], seed: number): Ad | null {
  if (pool.length === 0) return null;
  const total = pool.reduce((acc, a) => acc + Math.max(a.weight, 0), 0);
  if (total <= 0) return pool[0];
  let cursor = seed % total;
  for (const ad of pool) {
    cursor -= Math.max(ad.weight, 0);
    if (cursor < 0) return ad;
  }
  return pool[pool.length - 1];
}

// Deterministic-per-render with a per-request salt so Cloudflare's static
// cache doesn't pin a single creative to every visitor for an hour.
export function pickAd(
  slot: "left" | "right",
  saltSeed: number,
  preferClass?: AdClass
): Ad | null {
  const now = Date.now();
  const live = ALL_ADS.filter((a) => isLive(a, now) && fitsSlot(a, slot));

  // Priority: paid sponsor > exchange > house. If preferClass is set,
  // try that pool first; fall back to next class.
  const priority: AdClass[] = preferClass
    ? [
        preferClass,
        ...(["sponsor", "exchange", "house"] as AdClass[]).filter(
          (k) => k !== preferClass
        ),
      ]
    : ["sponsor", "exchange", "house"];

  for (const klass of priority) {
    const pool = live.filter((a) => a.klass === klass);
    if (pool.length > 0) return weightedPick(pool, saltSeed);
  }
  return null;
}

export function adClickUrl(adId: string): string {
  return `/api/ad/${encodeURIComponent(adId)}/click`;
}

export function getAdById(id: string): Ad | null {
  return ALL_ADS.find((a) => a.id === id) ?? null;
}
