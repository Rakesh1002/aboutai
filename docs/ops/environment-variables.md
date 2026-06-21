# Environment Variables — Validation Mode

## Active Bindings

Configured through `apps/frontend/wrangler.jsonc`:

- `DB` — D1 database binding.
- `RATELIMITS` — KV namespace for rate limiting.
- `EMAIL` — Cloudflare Email Sending binding.
- `ASSETS` — OpenNext assets binding.

## Active Vars

- `SITE_URL`
- `FROM_EMAIL`
- `FROM_NAME`
- `BULK_EMAIL_PROVIDER`

Current production-safe value:

```text
BULK_EMAIL_PROVIDER=none
```

## Optional Secrets

- `SESSION_SECRET` — signs validation-list session cookies.

## Deferred Secrets

Do not require these until the relevant feature exists and has passed validation:

- `RESEND_API_KEY`
- `ANTHROPIC_API_KEY`
- `CLERK_SECRET_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `RAZORPAY_WEBHOOK_SECRET`

---
**Owner:** Rakesh Roushan · **Last reviewed:** 2026-06-21 · **Review by:** 2026-09-21
