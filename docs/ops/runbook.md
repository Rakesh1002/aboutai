# Production Deployment — Validation Mode

**Status:** deploy the site as a validation list only. Do not treat deployment as public launch.

---

## Current Truth

- `apps/frontend/wrangler.jsonc` has D1, KV rate limiting, assets, and Cloudflare Email Sending bindings.
- `BULK_EMAIL_PROVIDER` is currently `none`.
- No production broadcast path should be claimed ready until a real test broadcast succeeds.
- No daily aggregation Workflow/cron should be claimed ready until it exists in code and Cloudflare.

---

## Safe Deploy Checks

```bash
cd apps/frontend
pnpm type-check
pnpm build
```

Cloudflare build/deploy, when ready:

```bash
pnpm cf:build
pnpm cf:deploy
```

---

## Smoke Tests

After deploy:

- `/` renders validation-list copy.
- `/daily` renders the no-public-dailies-yet state if no dailies are registered.
- `/archive` renders the no-public-teardowns-yet state if no essays are registered.
- `/stack` renders.
- `/stack.json` returns valid JSON.
- `POST /api/subscribe` succeeds against production bindings.
- Confirmation email arrives.
- Confirm link redirects to `/confirmed`.
- Unsubscribe link redirects to `/unsubscribed`.

Do not send a public issue until one private test broadcast has succeeded.

---
**Owner:** Rakesh Roushan · **Last reviewed:** 2026-06-21 · **Review by:** 2026-09-21
