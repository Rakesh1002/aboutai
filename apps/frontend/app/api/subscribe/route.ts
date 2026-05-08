import { NextRequest, NextResponse } from "next/server";
import { getEnv, newId, newToken, normalizeEmail, now } from "@/lib/cf";
import { buildConfirmEmail, sendTransactional } from "@/lib/email";

export const dynamic = "force-dynamic";

interface SubscribeRequest {
  email?: string;
  source?: string;
  utm_source?: string;
  utm_campaign?: string;
  utm_medium?: string;
}

const CONFIRM_TTL_SECONDS = 60 * 60 * 24 * 7;
const RATE_LIMIT_WINDOW_SECONDS = 60;
const RATE_LIMIT_MAX = 5;

async function rateLimit(env: CloudflareEnv, key: string): Promise<boolean> {
  const bucket = `rl:subscribe:${key}`;
  const current = await env.RATELIMITS.get(bucket);
  const count = current ? parseInt(current, 10) : 0;
  if (count >= RATE_LIMIT_MAX) return false;
  await env.RATELIMITS.put(bucket, String(count + 1), {
    expirationTtl: RATE_LIMIT_WINDOW_SECONDS,
  });
  return true;
}

export async function POST(req: NextRequest) {
  let body: SubscribeRequest;
  try {
    body = (await req.json()) as SubscribeRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const email = normalizeEmail(body.email ?? "");
  if (!email) {
    return NextResponse.json({ error: "Invalid email" }, { status: 400 });
  }

  const env = getEnv();

  const ip = req.headers.get("cf-connecting-ip") ?? "unknown";
  const country = req.headers.get("cf-ipcountry") ?? null;
  const ua = req.headers.get("user-agent")?.slice(0, 256) ?? null;

  if (!(await rateLimit(env, ip))) {
    return NextResponse.json(
      { error: "Too many attempts. Try again in a minute." },
      { status: 429 }
    );
  }

  const source = (body.source ?? "site").slice(0, 64);
  const confirmToken = newToken();
  const unsubscribeToken = newToken();
  const subscriberId = newId();
  const ts = now();
  const confirmExpires = ts + CONFIRM_TTL_SECONDS;

  const existing = await env.DB.prepare(
    "SELECT id, status FROM subscribers WHERE email = ?"
  )
    .bind(email)
    .first<{ id: string; status: string }>();

  let id = subscriberId;
  let activeConfirmToken = confirmToken;
  let activeUnsubToken = unsubscribeToken;

  if (!existing) {
    await env.DB.prepare(
      `INSERT INTO subscribers
       (id, email, status, source, confirm_token, confirm_token_expires,
        unsubscribe_token, created_at, utm_source, utm_campaign, utm_medium, ua, ip_country)
       VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
      .bind(
        subscriberId,
        email,
        source,
        confirmToken,
        confirmExpires,
        unsubscribeToken,
        ts,
        body.utm_source ?? null,
        body.utm_campaign ?? null,
        body.utm_medium ?? null,
        ua,
        country
      )
      .run();
  } else if (existing.status === "pending") {
    id = existing.id;
    await env.DB.prepare(
      `UPDATE subscribers
       SET confirm_token = ?, confirm_token_expires = ?
       WHERE id = ?`
    )
      .bind(confirmToken, confirmExpires, id)
      .run();
  } else if (existing.status === "confirmed") {
    return NextResponse.json({ ok: true, alreadyConfirmed: true });
  } else if (
    existing.status === "unsubscribed" ||
    existing.status === "bounced" ||
    existing.status === "suppressed"
  ) {
    id = existing.id;
    await env.DB.prepare(
      `UPDATE subscribers
       SET status = 'pending',
           confirm_token = ?,
           confirm_token_expires = ?,
           unsubscribed_at = NULL
       WHERE id = ?`
    )
      .bind(confirmToken, confirmExpires, id)
      .run();
    activeUnsubToken =
      (
        await env.DB.prepare(
          "SELECT unsubscribe_token AS t FROM subscribers WHERE id = ?"
        )
          .bind(id)
          .first<{ t: string }>()
      )?.t ?? unsubscribeToken;
  }

  void activeConfirmToken;
  void activeUnsubToken;

  const confirmUrl = `${env.SITE_URL}/api/confirm?token=${confirmToken}`;
  await sendTransactional(
    buildConfirmEmail({ email, confirmUrl }),
    "confirm",
    id
  );

  return NextResponse.json({ ok: true, status: "pending" });
}
