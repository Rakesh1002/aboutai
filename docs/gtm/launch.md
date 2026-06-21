# Launch Checklist — The AI Daily

**Status:** no-go for the May 26 public launch.  
**Mode:** validation list only until every P0 gate below is green.

---

## P0 Gates

- [ ] Remove all stale launch promises from public UI and email templates.
- [ ] Remove all placeholder/fake news from registered public content.
- [ ] Bank 4 daily issues with real sources and India-builder takeaways.
- [ ] Bank 2 Friday teardowns with screenshots/configs/cost/latency/what-broke/verdict.
- [ ] Verify `POST /api/subscribe` writes a pending subscriber row.
- [ ] Verify confirmation email arrives and `GET /api/confirm` confirms the subscriber.
- [ ] Verify `GET /api/unsubscribe` unsubscribes in one click.
- [ ] Verify one test broadcast path end to end before public sending.
- [ ] Confirm DNS, SPF, DKIM, and DMARC for the chosen sender.
- [ ] Confirm production deploy serves `/`, `/daily`, `/archive`, `/stack`, and `/stack.json`.

No public launch tweet, sponsor pitch, or paid tier work starts until all P0 gates are complete.

---

## Phase 1 Scope

Allowed:

- Homepage.
- Subscribe / confirm / unsubscribe.
- Daily rundown.
- Friday teardown.
- Archive list.
- Stack Mirror.

Blocked until validation passes:

- Paid archive.
- Member portal.
- Showcase / vendor directory.
- MCP server.
- Reports.
- Edge-rail ad sales.
- Automated daily aggregation claims.

---

## 30-Day Validation Targets

- 12+ daily issues shipped.
- 4 Friday teardowns shipped.
- 500-1,000 subscribers.
- 40%+ open rate.
- 1 real sponsor conversation or paid pilot.

Continue only if the strongest reader pull is for operator-seat teardowns. If the pull is generic AI news, fold into AudioPod content marketing.

---
**Owner:** Rakesh Roushan · **Last reviewed:** 2026-06-21 · **Review by:** 2026-09-21
