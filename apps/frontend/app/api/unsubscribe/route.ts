import { NextRequest, NextResponse } from "next/server";
import { getEnv, now } from "@/lib/cf";
import { buildUnsubscribeReceipt, sendTransactional } from "@/lib/email";

export const dynamic = "force-dynamic";

async function process(req: NextRequest, token: string) {
  if (!token || token.length < 16) {
    return NextResponse.redirect(
      new URL("/unsubscribed?status=invalid", req.url)
    );
  }

  const env = getEnv();
  const ts = now();

  const sub = await env.DB.prepare(
    `SELECT id, email, status FROM subscribers WHERE unsubscribe_token = ?`
  )
    .bind(token)
    .first<{ id: string; email: string; status: string }>();

  if (!sub) {
    return NextResponse.redirect(
      new URL("/unsubscribed?status=invalid", req.url)
    );
  }

  if (sub.status === "unsubscribed") {
    return NextResponse.redirect(
      new URL("/unsubscribed?status=already", req.url)
    );
  }

  await env.DB.prepare(
    `UPDATE subscribers
     SET status = 'unsubscribed',
         unsubscribed_at = ?
     WHERE id = ?`
  )
    .bind(ts, sub.id)
    .run();

  // Best-effort receipt; ignore failures so unsubscribe always succeeds.
  try {
    await sendTransactional(
      buildUnsubscribeReceipt({ email: sub.email }),
      "unsubscribe_receipt",
      sub.id
    );
  } catch {
    // ignore
  }

  return NextResponse.redirect(new URL("/unsubscribed?status=ok", req.url));
}

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token") ?? "";
  return process(req, token);
}

// One-click unsubscribe per RFC 8058: mail clients POST to the
// List-Unsubscribe URL when the user clicks the inbox-level button.
export async function POST(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token") ?? "";
  return process(req, token);
}
