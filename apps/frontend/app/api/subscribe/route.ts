import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

interface SubscribeRequest {
  email?: string;
  source?: string;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(req: NextRequest) {
  let body: SubscribeRequest;
  try {
    body = (await req.json()) as SubscribeRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const email = (body.email ?? "").trim().toLowerCase();
  const source = (body.source ?? "site").slice(0, 64);

  if (!email || !EMAIL_RE.test(email)) {
    return NextResponse.json({ error: "Invalid email" }, { status: 400 });
  }

  const apiKey = process.env.BEEHIIV_API_KEY;
  const publicationId = process.env.BEEHIIV_PUBLICATION_ID;

  if (!apiKey || !publicationId) {
    console.warn(
      "[subscribe] Beehiiv env not configured; logging signup only:",
      { email, source }
    );
    return NextResponse.json({ ok: true, logged: true });
  }

  const beehiivRes = await fetch(
    `https://api.beehiiv.com/v2/publications/${publicationId}/subscriptions`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        send_welcome_email: true,
        utm_source: source,
        reactivate_existing: false,
      }),
    }
  );

  if (!beehiivRes.ok) {
    const text = await beehiivRes.text();
    console.error("[subscribe] Beehiiv error", beehiivRes.status, text);
    return NextResponse.json(
      { error: "Subscription failed" },
      { status: 502 }
    );
  }

  return NextResponse.json({ ok: true });
}
