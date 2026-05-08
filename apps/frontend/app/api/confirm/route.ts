import { NextRequest, NextResponse } from "next/server";
import { getEnv, now } from "@/lib/cf";
import { buildWelcomeEmail, sendTransactional } from "@/lib/email";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token") ?? "";
  if (!token || token.length < 16) {
    return NextResponse.redirect(
      new URL("/confirmed?status=invalid", req.url)
    );
  }

  const env = getEnv();
  const ts = now();

  const sub = await env.DB.prepare(
    `SELECT id, email, status, unsubscribe_token, confirm_token_expires
     FROM subscribers WHERE confirm_token = ?`
  )
    .bind(token)
    .first<{
      id: string;
      email: string;
      status: string;
      unsubscribe_token: string;
      confirm_token_expires: number;
    }>();

  if (!sub) {
    return NextResponse.redirect(
      new URL("/confirmed?status=invalid", req.url)
    );
  }

  if (sub.status === "confirmed") {
    return NextResponse.redirect(
      new URL("/confirmed?status=already", req.url)
    );
  }

  if (sub.confirm_token_expires && sub.confirm_token_expires < ts) {
    return NextResponse.redirect(
      new URL("/confirmed?status=expired", req.url)
    );
  }

  await env.DB.prepare(
    `UPDATE subscribers
     SET status = 'confirmed',
         confirmed_at = ?,
         confirm_token = NULL,
         confirm_token_expires = NULL
     WHERE id = ?`
  )
    .bind(ts, sub.id)
    .run();

  const unsubscribeUrl = `${env.SITE_URL}/api/unsubscribe?token=${sub.unsubscribe_token}`;
  await sendTransactional(
    buildWelcomeEmail({
      email: sub.email,
      unsubscribeUrl,
      siteUrl: env.SITE_URL,
    }),
    "welcome",
    sub.id
  );

  return NextResponse.redirect(new URL("/confirmed?status=ok", req.url));
}
