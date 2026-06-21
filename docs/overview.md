---
rros_project: aboutai
rros_doc_id: aboutai/docs/overview.md
notion_page_id: 386e4a4b-2a11-81ee-b6d1-dacf1ec160d2
rros_domain: overview
---

# The AI Daily — Overview
> **One-liner:** A validation-stage publication for Indian AI builders, led by operator-seat teardowns of 30 production AI stacks; the daily brief is habit support, not the moat.
The single cold-start doc. A teammate should read this and know what this is, how to
run it, and the decisions that shaped it — in under 30 minutes.
## What & why
- **Problem:** Indian AI builders get generic AI news, but little real operator evidence — actual configs, costs, latency, what broke, and verdicts from production stacks.
- **Who it's for:** Indian AI builders, founders, and operators.
- **What we're building:** A daily AI rundown (Mon-Thu) plus a Friday operator-seat teardown drawn from 30 production stacks, with a Stack Mirror surface. The Friday teardown is the wedge; the daily brief drives habit and distribution.
- **Stage:** active (validation stage — not cleared for public launch).
- **Status right now:** Repo configured for a controlled validation list. Frontend (Next.js on Cloudflare via OpenNext) builds and serves public surfaces. Bulk email is intentionally `none` (not Resend/Workflows-ready). The May 26 public launch and the \$10K-MRR-by-November plan are explicitly no-go.
## How to run it
```bash
cd apps/frontend
pnpm install
pnpm dev
```
Useful checks and deploy commands (from `apps/frontend/package.json`):
```bash
pnpm type-check                 # tsc --noEmit
pnpm build                      # next build
pnpm cf:build                   # opennextjs-cloudflare build
pnpm cf:preview                 # opennextjs-cloudflare preview
pnpm cf:deploy                  # opennextjs-cloudflare deploy
pnpm db:apply:local             # wrangler d1 migrations apply aboutai --local
pnpm db:apply:remote            # wrangler d1 migrations apply aboutai --remote
```
- **Prod URL:** [https://theaidaily.in](https://theaidaily.in)
- **Repo:** [https://github.com/Rakesh1002/aboutai](https://github.com/Rakesh1002/aboutai)
- **Deploy:** Cloudflare (Worker `theaidaily`, `main` = `.open-next/worker.js`) via OpenNext (`opennextjs-cloudflare deploy`). Bindings configured in `apps/frontend/wrangler.jsonc`.
## Where things are
<table header-row="true">
<tr>
<td>Area</td>
<td>Location</td>
</tr>
<tr>
<td>Frontend / app</td>
<td>`apps/frontend/` (Next.js, MDX content)</td>
</tr>
<tr>
<td>API routes</td>
<td>`apps/frontend` — `/api/subscribe`, `/api/confirm`, `/api/unsubscribe`</td>
</tr>
<tr>
<td>Content registry</td>
<td>`apps/frontend/lib/content.ts` (only banked, human-reviewed content)</td>
</tr>
<tr>
<td>Infra / config</td>
<td>`apps/frontend/wrangler.jsonc` (D1 `aboutai`, KV `RATELIMITS`, Email Sending `EMAIL`, assets)</td>
</tr>
<tr>
<td>Docs</td>
<td>`docs/` (this canonical structure)</td>
</tr>
</table>
## Top 5 decisions to know
1. No public launch until validation gates pass — the May 26 launch and \$10K MRR plan are no-go → \[\[verdict-2026-04-27\]\]
2. The wedge is operator-seat teardowns from 30 production stacks, not generic AI news → \[\[thesis\]\]
3. Cloudflare-native stack (Next.js + OpenNext, D1, KV, Email Sending); bulk email deferred (`BULK_EMAIL_PROVIDER=none`) → \[\[architecture\]\]
4. Phase 1 scope is locked: homepage, subscribe/confirm/unsubscribe, daily, Friday teardown, archive, Stack Mirror — everything else deferred → \[\[prd\]\]
5. Kill rule: fold into AudioPod content marketing if teardowns do not out-pull generic AI news → \[\[roadmap\]\]
## Key links
- **Strategy:** \[\[thesis\]\] · **Market:** \[\[market\]\] · **Architecture:** \[\[architecture\]\] · **PRD:** \[\[prd\]\] · **Roadmap:** \[\[roadmap\]\]
- **Launch gates:** \[\[launch\]\] · **Runbook:** \[\[runbook\]\] · **Verdict / kill memo:** \[\[verdict-2026-04-27\]\]
---
**Owner:** Rakesh Roushan · **Last reviewed:** 2026-06-21 · **Review by:** 2026-09-21
