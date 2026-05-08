import { getEnv, newId, now } from "./cf";

export type EmailType =
  | "confirm"
  | "welcome"
  | "unsubscribe_receipt"
  | "broadcast";

interface SendArgs {
  to: string;
  subject: string;
  html: string;
  text: string;
  unsubscribeUrl?: string;
}

interface SendResult {
  ok: boolean;
  messageId?: string;
  errorCode?: string;
  errorMessage?: string;
  provider: "cf-email" | "noop";
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function wrapHtml(args: { preheader: string; bodyHtml: string }): string {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>The AI Teardown</title>
  </head>
  <body style="margin:0;padding:0;background:#fafafa;color:#18181b;font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
    <span style="display:none!important;color:transparent;visibility:hidden;height:0;width:0;">${escapeHtml(args.preheader)}</span>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td align="center" style="padding:32px 16px;">
        <table role="presentation" width="560" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;background:#fff;border:1px solid #e4e4e7;border-radius:8px;">
          <tr><td style="padding:32px;">
            ${args.bodyHtml}
          </td></tr>
        </table>
        <p style="font-size:12px;color:#71717a;margin-top:24px;">
          Sent by The AI Teardown · Bangalore · written by Rakesh Roushan
        </p>
      </td></tr>
    </table>
  </body>
</html>`;
}

export async function sendTransactional(
  args: SendArgs,
  type: EmailType,
  subscriberId: string
): Promise<SendResult> {
  const env = getEnv();

  const headers: Record<string, string> = {};
  if (args.unsubscribeUrl) {
    headers["List-Unsubscribe"] = `<${args.unsubscribeUrl}>`;
    headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click";
  }

  let result: SendResult;
  try {
    const response = await env.EMAIL.send({
      to: args.to,
      from: { email: env.FROM_EMAIL, name: env.FROM_NAME },
      subject: args.subject,
      html: args.html,
      text: args.text,
      headers: Object.keys(headers).length > 0 ? headers : undefined,
    });
    result = {
      ok: true,
      messageId: response.messageId,
      provider: "cf-email",
    };
  } catch (error) {
    const e = error as { code?: string; message?: string };
    result = {
      ok: false,
      errorCode: e.code,
      errorMessage: e.message,
      provider: "cf-email",
    };
  }

  await env.DB.prepare(
    `INSERT INTO send_events (id, subscriber_id, email_type, message_id, sent_at, status, provider, error_code, error_message)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(
      newId(),
      subscriberId,
      type,
      result.messageId ?? null,
      now(),
      result.ok ? "sent" : "failed",
      result.provider,
      result.errorCode ?? null,
      result.errorMessage ?? null
    )
    .run();

  return result;
}

export function buildConfirmEmail(args: {
  email: string;
  confirmUrl: string;
}): SendArgs {
  const preheader =
    "Confirm your subscription to The AI Teardown — one click, one teardown a week.";
  const bodyHtml = `
    <h1 style="font-size:22px;margin:0 0 16px;color:#18181b;">Confirm your subscription</h1>
    <p style="margin:0 0 16px;">You asked to subscribe to <strong>The AI Teardown</strong> — one honest AI tool teardown a week, written from running 30 production AI stacks.</p>
    <p style="margin:0 0 24px;">Click the button below to confirm. (If you didn't sign up, just ignore this email — you're not on the list.)</p>
    <p style="margin:0 0 24px;">
      <a href="${args.confirmUrl}" style="display:inline-block;background:#18181b;color:#fff;text-decoration:none;padding:12px 20px;border-radius:8px;font-weight:600;">Confirm subscription</a>
    </p>
    <p style="font-size:13px;color:#71717a;margin:0 0 8px;">Or paste this link into your browser:</p>
    <p style="font-size:13px;color:#52525b;margin:0;word-break:break-all;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;">${escapeHtml(args.confirmUrl)}</p>
  `;
  const text =
    `Confirm your subscription to The AI Teardown.\n\n` +
    `The AI Teardown is one honest AI tool teardown a week, written from running 30 production AI stacks.\n\n` +
    `Confirm here:\n${args.confirmUrl}\n\n` +
    `If you didn't sign up, just ignore this email — you're not on the list.\n`;
  return {
    to: args.email,
    subject: "Confirm your subscription to The AI Teardown",
    html: wrapHtml({ preheader, bodyHtml }),
    text,
  };
}

export function buildWelcomeEmail(args: {
  email: string;
  unsubscribeUrl: string;
  siteUrl: string;
}): SendArgs {
  const preheader =
    "You're in. First teardown drops Friday May 22, 2026 — IST morning.";
  const bodyHtml = `
    <h1 style="font-size:22px;margin:0 0 16px;color:#18181b;">You're in.</h1>
    <p style="margin:0 0 16px;">Thanks for subscribing to <strong>The AI Teardown</strong>. Here's what to expect:</p>
    <ul style="margin:0 0 16px;padding-left:20px;color:#27272a;">
      <li style="margin:0 0 8px;">One long-form teardown of a real AI tool, every Friday morning IST.</li>
      <li style="margin:0 0 8px;">Screenshots, configs, latency numbers, billing line items — receipts only.</li>
      <li style="margin:0 0 8px;">A three-state verdict: <em>Ship it</em>, <em>Trial only</em>, or <em>Avoid</em>.</li>
      <li style="margin:0 0 8px;">No affiliates, no hype, no sponsored conclusions.</li>
    </ul>
    <p style="margin:0 0 16px;">First teardown drops <strong>Friday May 22, 2026</strong>: <em>"What we ripped out of 30 startups in Q1 2026."</em></p>
    <p style="margin:0 0 16px;">In the meantime, the live Stack Mirror — every AI tool I'm currently running across the portfolio — is at <a href="${args.siteUrl}/stack" style="color:#18181b;">${escapeHtml(args.siteUrl)}/stack</a>.</p>
    <p style="margin:24px 0 0;color:#71717a;font-size:13px;">— Rakesh</p>
  `;
  const text =
    `You're in.\n\n` +
    `Thanks for subscribing to The AI Teardown. Here's what to expect:\n\n` +
    `- One long-form teardown of a real AI tool, every Friday morning IST.\n` +
    `- Screenshots, configs, latency numbers, billing line items.\n` +
    `- A three-state verdict: Ship it, Trial only, or Avoid.\n` +
    `- No affiliates, no hype, no sponsored conclusions.\n\n` +
    `First teardown drops Friday May 22, 2026: "What we ripped out of 30 startups in Q1 2026."\n\n` +
    `Live Stack Mirror: ${args.siteUrl}/stack\n\n` +
    `— Rakesh\n\n` +
    `Unsubscribe: ${args.unsubscribeUrl}\n`;
  return {
    to: args.email,
    subject: "You're in — welcome to The AI Teardown",
    html: wrapHtml({ preheader, bodyHtml }),
    text,
    unsubscribeUrl: args.unsubscribeUrl,
  };
}

export function buildUnsubscribeReceipt(args: { email: string }): SendArgs {
  const preheader = "You've been unsubscribed from The AI Teardown.";
  const bodyHtml = `
    <h1 style="font-size:22px;margin:0 0 16px;color:#18181b;">Unsubscribed.</h1>
    <p style="margin:0 0 16px;">You won't get any more emails from The AI Teardown. No follow-ups, no "are you sure" sequence.</p>
    <p style="margin:0 0 16px;color:#71717a;font-size:13px;">If this was a mistake, you can resubscribe any time at the homepage.</p>
  `;
  const text =
    `Unsubscribed.\n\n` +
    `You won't get any more emails from The AI Teardown. No follow-ups, no "are you sure" sequence.\n\n` +
    `If this was a mistake, resubscribe at the homepage.\n`;
  return {
    to: args.email,
    subject: "You've been unsubscribed from The AI Teardown",
    html: wrapHtml({ preheader, bodyHtml }),
    text,
  };
}
