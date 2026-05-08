// Manual fallback env shape. Run `npm run cf:types` after configuring
// wrangler.jsonc with real D1 / KV ids to regenerate `worker-configuration.d.ts`
// from the bindings — that file will override this one.

import type {
  D1Database,
  KVNamespace,
  Fetcher,
  SendEmail,
} from "@cloudflare/workers-types";

declare global {
  interface CloudflareEnv {
    DB: D1Database;
    EMAIL: SendEmail;
    RATELIMITS: KVNamespace;
    ASSETS: Fetcher;

    SITE_URL: string;
    FROM_EMAIL: string;
    FROM_NAME: string;
    BULK_EMAIL_PROVIDER: "none" | "resend" | "ses";
    RESEND_API_KEY?: string;
    SESSION_SECRET?: string;
  }
}

export {};
