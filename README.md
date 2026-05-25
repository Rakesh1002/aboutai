# The AI Daily

> Validation-stage publication for Indian AI builders. The wedge is operator-seat teardowns from 30 production stacks; the daily brief is support, not the moat.

The AI Daily is **not cleared for public launch yet**. The previous May 26 launch plan and $10K MRR-by-November plan are treated as no-go. The current repo is configured for a controlled validation list while content, email delivery, and cadence proof are prepared.

**No affiliates. No hype. No sponsored conclusions.**

---

## Current Decision

**No-go:** full public venture launch on 2026-05-26.

**Conditional go:** a 30-day validation sprint after launch blockers are fixed.

The venture continues only if operator-seat teardown content proves real pull. If generic AI news performs better than production teardowns, fold the writing into AudioPod content marketing.

---

## Validation Gates

Public sending starts only after:

- 4 daily issues are banked, sourced, human-edited, and ready to publish.
- 2 Friday teardowns are banked with real receipts from the 30-stack operator seat.
- Signup, confirmation email, unsubscribe, and one test broadcast are verified end to end.
- Stale launch dates and placeholder/fake news are absent from public surfaces.
- Phase 1 scope is limited to homepage, subscribe, daily, Friday teardown, archive list, and Stack Mirror.

30-day validation targets:

- 12+ dailies shipped.
- 4 teardowns shipped.
- 500-1,000 subscribers.
- 40%+ open rate.
- 1 real sponsor conversation or paid pilot.

---

## Scope

### In Phase 1

- Homepage and validation signup.
- Daily rundown pages.
- Friday teardown pages.
- Archive list.
- Stack Mirror (`/stack` and `/stack.json`).
- Subscriber confirmation and unsubscribe flows.

### Out Until Validation Passes

- Paid archive.
- Member portal.
- Showcase / vendor directory.
- MCP server.
- Edge-rail ad sales.
- Reports and paid Q&A.
- Broad $10K MRR execution plan.

---

## Repo Layout

```text
baku/
├── apps/frontend/           # Next.js app on Cloudflare Pages via OpenNext
├── strategy/                # Business/product/operator strategy
├── docs/                    # Engineering and launch runbooks
└── .context/                # Local collaboration notes
```

---

## Frontend

```bash
cd apps/frontend
pnpm install
pnpm dev
```

Useful checks:

```bash
pnpm type-check
pnpm build
```

Cloudflare resources are configured in `apps/frontend/wrangler.jsonc`. Current bulk email provider is intentionally `none`; do not claim Resend/Workflows readiness until implemented and tested.

---

## Source Of Truth

- `strategy/business/thesis.md` — validation-stage business thesis and current go/no-go decision.
- `strategy/product/prd.md` — product scope and phase gates.
- `strategy/platform-execution-plan.md` — 30-day validation execution plan.
- `strategy/verdict-2026-04-27.md` — original kill memo plus reality-check addenda.
- `docs/launch/LAUNCH_CHECKLIST.md` — launch blockers that must be cleared before public sending.

---

## License

Proprietary — All rights reserved.
