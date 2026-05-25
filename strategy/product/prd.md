# The AI Daily — Validation PRD

**Date:** 2026-05-24  
**Decision:** no public launch until readiness gates pass.

---

## 1. Product One-Liner

A validation-stage publication for Indian AI builders that tests whether production-stack AI tool teardowns create enough pull to justify a daily publication.

---

## 2. Phase 1 Surfaces

| Surface | Route | Required behavior |
|---|---|---|
| Home / validation signup | `/` | Explains validation status, captures email, does not promise a fixed launch date |
| Daily index | `/daily` | Shows published dailies or a no-public-dailies-yet state |
| Daily issue | `/daily/[date]` | Renders only registered, human-reviewed dailies |
| Teardown reader | `/[slug]` | Renders only registered teardowns |
| Archive | `/archive` | Lists teardowns or a no-public-teardowns-yet state |
| Stack Mirror | `/stack`, `/stack.json` | Shows current stack data |
| Email lifecycle | `/api/subscribe`, `/api/confirm`, `/api/unsubscribe`, `/confirmed`, `/unsubscribed` | Supports validation-list subscription, confirmation, and one-click unsubscribe |

---

## 3. Non-Goals Until Validation Passes

- Paid archive.
- Member portal.
- Showcase or vendor directory.
- MCP server.
- Reports.
- Edge-rail ad sales.
- Automated daily aggregation claims.
- Public $10K MRR roadmap.

---

## 4. Readiness Criteria

The product is not public-launch-ready until:

- 4 daily issues are banked.
- 2 Friday teardowns are banked.
- No stale May 12 / May 22 promises are visible in app or email copy.
- No placeholder/fake news is registered as published content.
- Signup, confirmation, unsubscribe, and one test broadcast are verified end to end.

---

## 5. Validation Success Criteria

Within 30 days of starting public sends:

- 12+ dailies ship.
- 4 teardowns ship.
- 500-1,000 subscribers join.
- Open rate is 40%+.
- At least 1 sponsor conversation or paid pilot occurs.

Qualitative pass condition: teardown content must drive stronger replies, shares, and conversions than generic AI news.

---

## 6. UX Copy Rules

- Use "validation list" until readiness gates pass.
- Do not promise a date until content and delivery are ready.
- Do not show sample news as real news.
- Do not advertise paid products before validation.
- Keep the reader promise centered on production receipts: screenshots, configs, costs, latency, what broke, and verdict.
