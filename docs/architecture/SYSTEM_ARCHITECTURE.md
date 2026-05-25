# System Architecture — Validation Mode

**Status:** minimal Cloudflare-native publication stack. The architecture intentionally excludes unvalidated Phase 2/3 products.

---

## Current Stack

- Frontend: Next.js app in `apps/frontend`.
- Runtime/deploy target: Cloudflare Pages via OpenNext.
- Database: D1 binding `DB`, database name `aboutai`.
- Rate limiting: KV binding `RATELIMITS`.
- Email: Cloudflare Email Sending binding `EMAIL` for transactional messages.
- Bulk email: not implemented; `BULK_EMAIL_PROVIDER` is `none`.
- Content: registered daily modules and MDX essays in repo.

---

## Public Routes

- `/`
- `/daily`
- `/daily/[date]`
- `/archive`
- `/[slug]`
- `/stack`
- `/stack.json`
- `/confirmed`
- `/unsubscribed`

## API Routes

- `POST /api/subscribe`
- `GET /api/confirm`
- `GET /api/unsubscribe`

---

## Deferred Architecture

Do not document or build these as active architecture until validation passes:

- Automated daily aggregation Workflow/cron.
- Resend or SES broadcast pipeline.
- Paid archive and auth.
- Stripe/Razorpay billing.
- Vector search / archive Q&A.
- Showcase / vendor directory.
- MCP server.
- Browser Rendering automation.

---

## Content Safety Rule

Only banked, human-reviewed content is registered in `lib/content.ts`. Drafts may live in the repo, but they must not be included in public content arrays until they are ready to publish.
