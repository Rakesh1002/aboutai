// HMAC-signed session cookie. Stateless — no D1 lookup on every page render.
// Format: <subscriberId>.<tier>.<exp>.<sigHex>
//
// Why not JWT: we don't need claim flexibility. A single-purpose
// signed string is smaller, faster, and harder to misuse. We also avoid
// the JWT alg-confusion class of vulnerabilities entirely.

const COOKIE_NAME = "tad_session";
const SESSION_DURATION_SEC = 60 * 60 * 24 * 365; // 1 year

export type SessionTier = "free" | "paid" | "founder";

export interface Session {
  subscriberId: string;
  tier: SessionTier;
  exp: number;
}

async function getKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

async function sign(payload: string, secret: string): Promise<string> {
  const key = await getKey(secret);
  const sig = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(payload)
  );
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

async function verify(
  payload: string,
  sigHex: string,
  secret: string
): Promise<boolean> {
  const expected = await sign(payload, secret);
  return timingSafeEqual(expected, sigHex);
}

const ALLOWED_TIERS: SessionTier[] = ["free", "paid", "founder"];

export async function createSession(
  subscriberId: string,
  tier: SessionTier,
  secret: string,
  ttlSec: number = SESSION_DURATION_SEC
): Promise<string> {
  const exp = Math.floor(Date.now() / 1000) + ttlSec;
  const payload = `${subscriberId}.${tier}.${exp}`;
  const sig = await sign(payload, secret);
  return `${payload}.${sig}`;
}

export async function readSession(
  cookieValue: string | undefined,
  secret: string
): Promise<Session | null> {
  if (!cookieValue) return null;
  const parts = cookieValue.split(".");
  if (parts.length !== 4) return null;
  const [subscriberId, tier, expStr, sig] = parts;
  if (!subscriberId || !tier || !expStr || !sig) return null;
  if (!(ALLOWED_TIERS as string[]).includes(tier)) return null;
  const exp = parseInt(expStr, 10);
  if (!exp || exp < Math.floor(Date.now() / 1000)) return null;
  const payload = `${subscriberId}.${tier}.${expStr}`;
  if (!(await verify(payload, sig, secret))) return null;
  return { subscriberId, tier: tier as SessionTier, exp };
}

interface CookieAttrs {
  name: string;
  value: string;
  path: string;
  httpOnly: boolean;
  secure: boolean;
  sameSite: "lax" | "strict" | "none";
  maxAge: number;
}

export function buildSessionCookieAttrs(
  value: string,
  ttlSec: number = SESSION_DURATION_SEC
): CookieAttrs {
  return {
    name: COOKIE_NAME,
    value,
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: ttlSec,
  };
}

export function serializeCookie(attrs: CookieAttrs): string {
  const parts = [
    `${attrs.name}=${attrs.value}`,
    `Path=${attrs.path}`,
    `Max-Age=${attrs.maxAge}`,
    `SameSite=${attrs.sameSite[0].toUpperCase() + attrs.sameSite.slice(1)}`,
  ];
  if (attrs.httpOnly) parts.push("HttpOnly");
  if (attrs.secure) parts.push("Secure");
  return parts.join("; ");
}

export const SESSION_COOKIE_NAME = COOKIE_NAME;
