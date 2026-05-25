import { getEnv } from "@/lib/cf";

// Constant-time comparison to avoid timing leaks on token check.
function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export interface AuthResult {
  ok: boolean;
  reason?: "missing_secret" | "missing_token" | "bad_token";
}

// Two roles:
//   - cron: uses CRON_SECRET, can run the pipeline + read drafts.
//   - admin: uses ADMIN_TOKEN, can also flip statuses + manage sources.
// Either token in the Authorization header is accepted; admin is a superset.
export function checkAggregatorAuth(
  req: Request,
  level: "cron" | "admin"
): AuthResult {
  const env = getEnv() as unknown as {
    CRON_SECRET?: string;
    ADMIN_TOKEN?: string;
  };

  const auth = req.headers.get("authorization") ?? "";
  const presented = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!presented) return { ok: false, reason: "missing_token" };

  const adminToken = env.ADMIN_TOKEN;
  if (adminToken && constantTimeEqual(presented, adminToken)) {
    return { ok: true };
  }

  if (level === "cron") {
    const cronSecret = env.CRON_SECRET;
    if (!cronSecret) return { ok: false, reason: "missing_secret" };
    if (constantTimeEqual(presented, cronSecret)) return { ok: true };
  }

  return { ok: false, reason: "bad_token" };
}
