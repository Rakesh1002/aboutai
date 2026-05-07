# aboutai — Platform Execution Plan

**Date:** 2026-05-08
**Operator:** Rakesh Roushan, solo
**Brand:** `aboutai` (kept — supports the AI-tool-teardown persona; no rename)
**Companion docs:** `strategy/verdict-2026-04-27.md` (the venture verdict + wedge thesis)
**Status:** This is the operating plan, not a strategy memo. Every line is an action.

---

## 0. The thesis in one paragraph

Build a defensible publishing platform — newsletter at the front, a custom CMS + member system + sponsored-showcase platform underneath — anchored on one weekly artifact only Rakesh can produce: rigorous, evidence-backed AI-tool teardowns from running 30 production AI stacks. Phase 1 (M0–M3) ships on Beehiiv with a custom Next.js front because building email infra before having readers is the classic founder mistake. Phase 2 (M3–M6) migrates to a fully owned platform on Cloudflare once the cadence is proven and revenue justifies infra time. Phase 3 (M6–M18) layers a sponsored Showcase, paid tiers, vendor verification, and a Stack Mirror data product on top of the same platform. Newsletter is the wedge; platform is the moat.

---

## 1. Phase 1 — M0–M3 (May 8 to Aug 8, 2026): Cadence, not infra

### Why Beehiiv first, not custom

| Factor | Beehiiv (M0–M3) | Custom platform (M0–M3) |
|--------|-----------------|--------------------------|
| Cost at <2,500 subs | **$0** (free tier) | ~$30–80/mo (Resend/SES + R2 + DO) — small but real |
| Time to first send | **30 minutes** | 2–3 weeks of email infra work |
| Deliverability | **Inherited** (warm IPs, DMARC, list-cleaning, spam-trap rotation) | Cold IPs, ramp-up risk, ~3-6 months to match |
| Beehiiv Ad Network | **Ready** at any list size | n/a |
| beehiiv Boosts (paid sub acquisition) | **Available** | n/a, you'd need to build it |
| Customization (paywall, showcase) | Limited | Unlimited |

**The discipline:** every hour spent on email infra in M0–M3 is an hour not spent writing teardowns. The single biggest predictor of the venture surviving is shipping 12 essays in 12 weeks. Beehiiv is rented sending; the list itself is yours (CSV-exportable from day one). Phase 2 buys the migration.

### The hybrid architecture in Phase 1

```
              ┌────────────────────────────────────────────────────┐
              │                  aboutai.com                      │
              │     (Next.js on Cloudflare Pages, OpenNext)        │
              │                                                    │
              │  /         landing + email capture                 │
              │  /[slug]   essay reader (MDX in repo)              │
              │  /stack    Stack Mirror v0 (static page + JSON)    │
              │  /archive  list of essays                          │
              │  /api/subscribe  → POST to Beehiiv API             │
              └────────────────────────────────────────────────────┘
                                      │
                             subscribe writes go here
                                      ▼
              ┌────────────────────────────────────────────────────┐
              │                Beehiiv (rented)                    │
              │   • subscriber storage  • email send                │
              │   • open/click tracking • ad network                │
              │   • Boosts cross-promo  • RSS-to-email              │
              └────────────────────────────────────────────────────┘
```

- Essays live in `apps/frontend/content/essays/*.mdx` — version controlled, no CMS, you're one author.
- Each Friday: publish MDX, deploy site, Beehiiv pulls via RSS-to-email OR you copy-paste the essay into Beehiiv (RSS is faster but loses formatting; copy-paste is 10 minutes).
- Stack Mirror is a single `/stack` page driven by a YAML or JSON file in repo (`content/stack.json`). Update monthly, manually.
- Subscribe form on every page POSTs to `/api/subscribe`, a Worker route that calls Beehiiv's `/v2/subscriptions` API.

### Phase 1 monetization (4 streams, in order of arrival)

1. **Newsletter sponsorship** (target M2): one slot per Friday issue at $1,500 (rises to $3K when list crosses 25K). Sold direct via cold outreach to AI infra companies whose ICP = your reader (Modal, Helicone, LangSmith, Braintrust, BAML, Together AI, Outlines, Letta).
2. **Beehiiv Ad Network** (target M2): auto-fill any unsold slot. Net ~$0.20–$1 per 1K opens. Floor revenue, not headline.
3. **Paid newsletter tier** (target Aug 1): $25/mo or $240/yr. Two perks: full archive past 12 weeks, monthly group call. Use Beehiiv's native paid subs for Phase 1 (Stripe-backed, 2.5% platform fee). Rebuild on custom in Phase 2.
4. **One-time premium teardown** (target M3): single deep-investigation piece sold as a one-off PDF + interactive demo at $49 — e.g., *"30 AI Sales Agents, 30 Days: The Receipts."* This is the appetizer for the paid tier and the proof-point that paywall conversion works.

**Phase 1 revenue target by Aug 8:** **$3K MRR floor / $5–8K MRR plausible.** Below $3K = fold the writing into AudioPod and stop.

---

## 2. Phase 2 — M3–M6 (Aug 8 to Nov 8, 2026): Own the platform

Trigger: ≥5K free subs AND ≥$3K MRR. If both gates hit, build the custom platform. If not, stay on Beehiiv and reconsider monthly.

### What Phase 2 unlocks that Beehiiv can't

- **Programmable paywall:** unlock individual essays at $5, full year at $240, founder tier at $1,500. Beehiiv only supports one paid tier.
- **Sponsored Showcase:** a curated, transparent vendor directory inside the site that uses your trust system and earns vendor placement fees — Beehiiv has nothing for this.
- **Stack Mirror Pro:** paid API access + MCP server for your portfolio's AI tool usage data. Custom-only.
- **Member portal:** profile, comments on essays, saved teardowns, monthly call attendance. Custom-only.
- **Embeddable widgets:** `Verified by aboutai` badges that vendors place on their sites — viral mechanic. Custom-only.
- **Cost discipline at scale:** Beehiiv at 100K subs ~$500/mo. Cloudflare Email Service + Workers at 100K subs ~$60–100/mo, fully owned.

### Phase 2 architecture (Cloudflare-native, inside your default stack)

```
                              ┌────────────────────────┐
                              │   Next.js on CF Pages  │
                              │      aboutai.com      │
                              └───────────┬────────────┘
                                          │
                              ┌───────────┴────────────┐
                              │  CF Workers + Hono     │
                              │  (api.aboutai.com)    │
                              └─┬──┬──┬──┬──┬──┬──┬──┬─┘
                                │  │  │  │  │  │  │  │
        ┌───────────────────────┘  │  │  │  │  │  │  └────────────┐
        │           ┌──────────────┘  │  │  │  │  └─────────┐     │
        │           │   ┌─────────────┘  │  │  └──────┐     │     │
        ▼           ▼   ▼                ▼  ▼         ▼     ▼     ▼
   ┌─────────┐ ┌────────────┐    ┌──────────────┐ ┌──────┐ ┌────────────┐
   │   D1    │ │     R2     │    │  Vectorize   │ │ Workers AI │ │ Workflows  │
   │subs/    │ │post images,│    │ archive      │ │ in-archive │ │ scheduled  │
   │posts/   │ │downloads,  │    │ semantic     │ │ Q&A for    │ │ sends,     │
   │vendors/ │ │PDF reports │    │ search       │ │ paid tier  │ │ billing    │
   │payments │ │            │    │              │ │            │ │ retries    │
   └─────────┘ └────────────┘    └──────────────┘ └────────────┘ └────────────┘

           ┌──────────────────────────┐    ┌────────────────────────────────┐
           │  Cloudflare Email Send   │    │   Clerk + Stripe + Razorpay   │
           │  Marketing + transactional│    │   auth + paid subs + India    │
           └──────────────────────────┘    └────────────────────────────────┘

           ┌──────────────────────────┐
           │  Browser Rendering       │
           │  automated screenshot    │
           │  capture for teardowns   │
           └──────────────────────────┘
```

### D1 schema (Phase 2 starting state)

```sql
-- subscribers (migrated from Beehiiv export)
CREATE TABLE subscribers (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL,                    -- active / unsubscribed / bounced
  source TEXT,                             -- launch / x / hn / boosts / referral
  subscribed_at INTEGER NOT NULL,
  utm_json TEXT,
  tier TEXT NOT NULL DEFAULT 'free',       -- free / paid / founder
  stripe_customer_id TEXT,
  razorpay_customer_id TEXT,
  clerk_user_id TEXT
);

CREATE TABLE posts (
  slug TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  excerpt TEXT,
  body_mdx TEXT NOT NULL,
  hero_image_r2_key TEXT,
  type TEXT NOT NULL,                      -- teardown / showcase / receipts / vertical / open_letter / report
  verdict TEXT,                            -- ship_it / trial_only / avoid / null
  paywall TEXT NOT NULL DEFAULT 'free',    -- free / paid / one_time
  one_time_price_cents INTEGER,
  published_at INTEGER,
  updated_at INTEGER NOT NULL,
  vendor_slugs TEXT,                       -- JSON array of related vendors
  tags TEXT                                -- JSON array
);

CREATE TABLE vendors (
  slug TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  homepage TEXT NOT NULL,
  category TEXT NOT NULL,                  -- inference / vector_db / observability / etc.
  classification TEXT,                     -- native / fine_tuned / rag_app / wrapper / unknown
  is_showcase BOOLEAN DEFAULT FALSE,
  showcase_tier TEXT,                      -- listed / featured / spotlight
  showcase_started_at INTEGER,
  showcase_ends_at INTEGER,
  trust_artifacts_json TEXT                -- screenshots, configs, latency, our notes
);

CREATE TABLE stack_entries (
  id TEXT PRIMARY KEY,
  startup_slug TEXT NOT NULL,              -- audiopod, flarecode, etc.
  vendor_slug TEXT NOT NULL,
  category TEXT NOT NULL,
  status TEXT NOT NULL,                    -- in_production / trialing / ripped_out
  started_at INTEGER,
  ended_at INTEGER,
  monthly_cost_cents INTEGER,
  notes TEXT
);

CREATE TABLE post_unlocks (
  id TEXT PRIMARY KEY,
  subscriber_id TEXT NOT NULL,
  post_slug TEXT NOT NULL,
  unlocked_at INTEGER NOT NULL,
  amount_cents INTEGER,
  payment_provider TEXT,                   -- stripe / razorpay / tier_grant
  UNIQUE(subscriber_id, post_slug)
);

CREATE TABLE sponsorships (
  id TEXT PRIMARY KEY,
  vendor_slug TEXT NOT NULL,
  type TEXT NOT NULL,                      -- newsletter_slot / showcase / sponsored_investigation
  starts_at INTEGER NOT NULL,
  ends_at INTEGER NOT NULL,
  amount_cents INTEGER NOT NULL,
  status TEXT NOT NULL                     -- pending / approved / live / ended / declined
);
```

### Phase 2 scope (what gets built)

1. **Migrate subscribers** out of Beehiiv into D1 (export CSV, dual-send for 4 weeks, cut over).
2. **Outbound email** via Cloudflare Email Service (Email Sending) for transactional + Resend or AWS SES for marketing-volume sends. Validate deliverability with a real warm-up period before cutover.
3. **Auth + billing:** Clerk + Stripe (global) + Razorpay (India UPI). Webhooks update D1.
4. **Paywall:** `paywall` column on `posts`. Server-side gate on `/[slug]` reader. Anonymous reader sees first 30% + a pay-to-unlock card with 3 options: $5 one-time, $25/mo, $240/yr.
5. **Member portal:** `/account` showing tier, archive, unlocks, calls attended.
6. **Search over archive:** Vectorize + Workers AI. Paid-only feature: "Ask the archive" — a chat interface that answers questions citing your essays.
7. **Monthly group call infra:** lightweight signup + Zoom/Riverside link for paid members.

---

## 3. Phase 3 — M6–M18 (Nov 2026 to Nov 2027): Sponsored Showcase + data products

Trigger: ≥15K free subs AND ≥$10K MRR.

### The Showcase: a paid directory that doesn't break trust

Futurepedia broke trust by selling the score. The aboutai rule:

> **Vendors pay for the audit. They never pay for the verdict.**

If a tool is a wrapper, you keep the money and publish the wrapper finding. This aligns vendor incentives toward genuinely improving the product before paying for re-audit, rather than buying a badge.

**Showcase tiers:**

| Tier | Price | What vendor gets | What reader gets |
|------|-------|------------------|------------------|
| **Listed** | $99 / month | Inclusion in `/showcase` directory, public trust card with classification (native / fine-tuned / RAG / wrapper), basic profile | A trustworthy directory of tools whose makers paid for the audit and accepted the verdict, however brutal |
| **Featured** | $499 / month | Above-fold in their category, expanded profile, link to their teardown if one exists | Up-front signal that someone serious enough to pay for audit also showed up for it |
| **Spotlight** | $1,999 / one-time | Sponsored deep teardown (clearly labeled, vendor doesn't see verdict before publish), permanent placement, social-card distribution | Long-form audit they wouldn't otherwise get; clear sponsored-but-honest label |
| **Verified Vendor (annual)** | $4,999 / year | Continuous monitoring of their tool, trust-card refreshed quarterly, "Verified by aboutai" embeddable badge for their own site | Highest-trust signal in the category |

**The hard rule on labels:** every Showcase listing carries the classification stamp — *Native AI* / *Fine-Tuned* / *RAG App* / *Wrapper* — visible at first glance. Wrappers are not blocked from listing; they just get labeled. Honesty IS the product.

**The viral mechanic:** the embeddable `Verified by aboutai` badge that vendors put on their own homepage links back to their trust card on `aboutai.com`. Each badge is free distribution.

### Stack Mirror Pro — the data product

The Stack Mirror at `/stack` is a moat. It says: "Here are the 30 AI-native startups Rakesh runs and exactly which AI tools each one uses in production right now." Update monthly, public diff posts each month.

**Free:** read-only HTML view + JSON feed at `/stack.json`.
**Pro ($499/mo for AI infra companies):** full historical timeline (every tool every startup ever ran, when added, when removed, why), category leaderboards, alerts when a competitor wins a slot, MCP server endpoint for their own internal AI agents to query.

The buyer of Stack Mirror Pro is the head of product at Modal / Helicone / Braintrust / Together AI / etc. — they want to know what real production AI stacks look like and would pay $5K/yr for a quarterly snapshot. aboutai has one of <50 such datasets in existence.

### Quarterly *State of AI Stacks* report

PDF + web report, $999 download or free for paid subs. Real data from your portfolio + survey data from your top-1K paid readers. Becomes link bait for journalists, VCs, founders. One per quarter, max.

---

## 4. Full monetization menu (what's in, what's out)

### IN — ship in this order

| # | Stream | Phase | Pricing | Realistic ARR ceiling at 50K subs |
|---|--------|-------|---------|-----------------------------------|
| 1 | Newsletter sponsorship (1 slot/issue) | P1 | $1.5–5K/issue | $250K |
| 2 | Beehiiv Ad Network fill | P1 | CPC-equivalent | $30K |
| 3 | Paid sub tier ($25/mo, $240/yr) | P1 → P2 | 2–4% conversion | $300K–600K |
| 4 | One-time premium teardowns/reports | P1 | $5–49 each | $50K |
| 5 | Founder tier ($1,500/yr, 50 seats max) | P2 | direct DM + quarterly review | $75K |
| 6 | Showcase Listed | P3 | $99/mo | $60K (50 vendors) |
| 7 | Showcase Featured | P3 | $499/mo | $60K (10 vendors) |
| 8 | Showcase Spotlight (sponsored teardown) | P3 | $1,999 each, ~6/yr | $12K |
| 9 | Verified Vendor annual | P3 | $4,999/yr | $100K (20 vendors) |
| 10 | Stack Mirror Pro API | P3 | $499/mo | $120K (20 buyers) |
| 11 | *State of AI Stacks* quarterly report | P3 | $999/dl | $50K |
| 12 | Live Run events (Twitter Spaces / YT Live) | P3 | sponsored $5K each | $40K |
| 13 | Custom benchmarks for vendors | P3 | $5–15K project | $60K |
| 14 | Pay-Per-Crawl (Cloudflare AI Crawl Control / TollBit) | P2 | per-crawl | $20K speculative |
| 15 | MCP server for vendor discovery (LLMs query aboutai) | P3 | $0.001/query metered | $30K speculative |

**Plausible total ARR at 50K subs:** $1.1M-$1.6M. **At 100K subs:** $2-3M.

### OUT — stay disciplined, refuse these

- ❌ **Pay-for-positive-verdict.** The thesis dies the day a Spotlight goes live with a vendor controlling the conclusion. This is the ONE inviolable rule. Every Spotlight has the contract clause: "aboutai retains full editorial control over verdict; vendor cannot review draft before publish."
- ❌ **Affiliate links.** Even one affiliate link nukes editorial trust. If you must, allow only post-teardown affiliate buttons for tools you scored `Ship it`, capped at 5% of revenue, fully disclosed, and never on items where the verdict is ambiguous.
- ❌ **Maven-style cohorts taught by you.** You don't have time. Defer or partner-only with rev share, after M12.
- ❌ **Open Discord/Circle community.** Ghost towns kill brand. Defer until 25K paid+free subs.
- ❌ **Generic display ads.** Banner ads on essays cheapen the brand for $50 CPM you don't need.
- ❌ **Recruitment / job board** — defer past M12, low ROI for early traffic.
- ❌ **Verified Listings without audit (Futurepedia model)** — directly contradicts the trust thesis.

---

## 5. Content type taxonomy (what gets published, how often)

| Type | Cadence | Length | Format | Paywall | Purpose |
|------|---------|--------|--------|---------|---------|
| **Teardown** (flagship) | 1/week, Friday | 1,500–2,500 words | MDX, screenshots, configs, verdict | Latest 12 weeks free; older paid | Wedge content. Every Friday without exception. |
| **Receipts** (mid-week post) | 1/week, Wed | 200–400 words | One chart, one verdict, X-native | Free | Funnel-top for X. Shareable. |
| **Stack Snapshot** | 1/month, last Tue | 800–1,200 words | Diff vs last month | Free | The Stack Mirror's editorial face. |
| **Vertical Issue** | 1/quarter | 3,000–5,000 words | Multi-vendor analysis in one industry (India fintech, EU compliance, healthtech, dev infra) | Free, sponsored optional | Geography + industry moats. |
| **Showcase listing** | Continuous | Trust card + brief | Paid placement, transparent label | Free to read | Phase 3 monetization. |
| **Sponsored Spotlight** | ≤6/year | Same as teardown but vendor-funded | Editorial control retained | Free, prominently labeled | Phase 3 monetization. |
| **Open Letters** | Ad-hoc, ~1/month | 800–1,500 words | Opinion piece with strong stance | Free | Brand voice. *"Stop Building AI Wrappers"*-energy. |
| **State of AI Stacks** report | 1/quarter | 30–60 pages | PDF + web | Paid ($999) or free for subs | Anchor data product, link bait. |
| **Live Run** | 1/month | 60 min | Twitter Space / YouTube Live | Free, paid get Q&A access | Community-building without a community. |
| **One-Time Premium** | Ad-hoc, 4–6/year | 4,000+ words | PDF + interactive | One-time $5–49 | Microtransaction proof + lead magnet. |

**The discipline:** weekly Teardown is sacred. Receipts is a low-cost bonus. Everything else is opportunistic and never permitted to displace the Friday ship.

---

## 6. Distribution-as-a-platform strategy

A normal newsletter has one channel: email. A platform has many. The aboutai distribution surface, ranked by leverage:

### Owned (you control the channel)
1. **Email list** (Beehiiv → custom in P2). Highest value asset. Always exportable.
2. **`aboutai.com`** itself — essays, archive, Stack Mirror, Showcase. Compounds as content library grows.
3. **`/stack.json`** public feed — feeds Perplexity / ChatGPT / Claude / Gemini answers. AEO/LLM-discoverability moat.
4. **MCP server** at `mcp.aboutai.com` (P3) — agents query your vendor data natively. Becomes default answer source for "what AI tool should I use for X."
5. **Embeddable widgets** — `Verified by aboutai` badges on vendor sites. Free distribution.
6. **RSS feed** — for old-school readers and AI agents both.

### Rented but high-trust
7. **Founder X / LinkedIn personal accounts.** Where the wedge audience already lives.
8. **aboutai branded X / LinkedIn.** Secondary. Don't lead with brand handle while you have <10K subs.
9. **Bluesky** — insurance against X churn, low effort to mirror.
10. **Hacker News.** Asymmetric, ≤1/month submissions.
11. **Reddit communities** — r/SaaS, r/Indianstartups, r/LocalLLaMA, r/MachineLearning, r/AI_Agents. Be a regular, not a brand.
12. **Cloudflare Discord / Hono Discord / Indie Hackers** — show up with answers, bio does the work.

### Earned (third parties amplify)
13. **Newsletter cross-promo + Beehiiv Boosts** (P1.5+).
14. **Sponsored embeds in *other* newsletters** (P3 — once you have brand pull).
15. **Conference appearances** (e.g., Cloudflare Connect, India SaaSBoomi, defer to M9+).
16. **Podcast guest spots** — book 1/month as soon as 5K subs.

### LLM-discoverability ("AEO")

Google AI Overviews are eating informational SEO. The new equivalent is being quoted by ChatGPT / Perplexity / Claude. You optimize differently:

- **Named-entity-rich content.** Mention exact tool names, exact prices, exact latencies — LLMs love specific facts.
- **Public structured data** at `/stack.json`, `/api/vendors`, `/api/teardowns` (read-only public endpoints).
- **`/llms.txt`** at site root listing the top 50 essays + Stack Mirror as authoritative entry points.
- **MCP server** — by P3, vendors and agents query aboutai directly.
- **Cloudflare Pay-Per-Crawl** (when GA at scale) — earn from being read by AI bots.
- **Pure server-side rendering** (no SPA hydration walls). Already covered by Next.js + OpenNext on CF Pages.

### Distribution decision tree (for any new piece of content)

```
Did the essay ship Friday?
├─ NO  → fix this first, nothing else matters.
└─ YES
   ├─ Did the X thread ship Friday at the same hour?
   │  ├─ NO → ship before lunch.
   │  └─ YES
   ├─ LinkedIn carousel ready?
   │  ├─ NO → ship Saturday morning.
   │  └─ YES
   ├─ Reddit cross-post on the *most relevant* subreddit (only one)?
   │  ├─ NO → ship Saturday afternoon.
   │  └─ YES
   ├─ Bluesky mirror?  → automate via cross-poster.
   ├─ HN (only if essay is technically deep enough)?
   │  └─ Tuesday morning, max one per month.
   └─ Personal email to 5 specific people you'd want as readers.
```

---

## 7. The 12-month phased roadmap

| Phase | Months | Goal | Tech | Revenue |
|-------|--------|------|------|---------|
| **P1: Cadence** | May–Aug 2026 | 5K subs, $3–5K MRR | Next.js on CF Pages + Beehiiv | newsletter sponsor + paid tier |
| **P2: Own the platform** | Aug–Nov 2026 | 15K subs, $10K MRR | + D1, R2, Workers, Clerk, Stripe, Razorpay, CF Email Service / Resend | + paywall, founder tier, premium reports |
| **P3: Showcase + data** | Nov 2026–May 2027 | 40K subs, $40K MRR | + Vectorize, Workers AI, MCP server, Browser Rendering automation | + Showcase tiers, Stack Mirror Pro, vendor verification, sponsored Spotlights |
| **P4: Scale** | May–Nov 2027 | 100K subs, $100K MRR | + multi-author CMS if hiring an editor; AI-co-author workflow for Receipts | + custom benchmarks, conference, partnership deals |

**Decision gates remain the same as the verdict doc:** miss two consecutive Friday sends → kill. Miss the M3 revenue floor → fold into AudioPod content marketing.

---

## 8. Architecture decisions to lock now (so Phase 2 migration is trivial)

Even though Phase 1 ships on Beehiiv, every Phase 1 decision must be made with Phase 2 in mind. Specifically:

1. **Don't use Beehiiv-hosted forms.** Use a custom form that POSTs to `/api/subscribe`, which then calls Beehiiv's API. This way, when you migrate, you change one line of code; subscribers never see an interruption.
2. **Capture full attribution** at signup time: source, UTMs, referrer, user-agent. Beehiiv stores this; you also write it into a `signups.csv` shadow log in R2 for safety.
3. **Essay content lives in MDX in repo, not in Beehiiv.** Beehiiv only ever gets a copy. The canonical post is at `aboutai.com/[slug]`. Beehiiv sends are pull-from-RSS or copy-paste only.
4. **Paid subs in Phase 1 use Beehiiv's Stripe-backed system.** Stripe customer IDs come back to you on export. Same Stripe account = no payment migration; just rebuild the gating logic.
5. **Use one canonical URL for everything.** No `email.aboutai.com` or `app.aboutai.com` micro-domains in P1. One brand, one domain, easier to consolidate later.
6. **Schema-design the Stack Mirror today** (`content/stack.json`) in the same shape as Phase 2's D1 `stack_entries` table. Then the Phase 2 migration is `cat content/stack.json | wrangler d1 execute --command "INSERT..."`.

---

## 9. The first 90 days — concrete dates

| Date | Action | Output |
|------|--------|--------|
| **Fri May 8** | Confirm `aboutai.com` + handles secured. Strip backend on `strip-and-rebrand` branch. | Branch shipped. Domain confirmed. |
| **Sat–Sun May 9–10** | Land new landing page (single email form). Beehiiv configured. `/api/subscribe` Worker live. | Landing page on staging. |
| **Mon–Thu May 11–14** | Pre-write essays #1–#4. | 4 MDX files in repo. |
| **Fri May 15** | Deploy to production at `aboutai.com`. Soft-launch on personal X. | Public site live. ~50–100 first subs. |
| **Mon May 18** | Public launch tweet. Reply-guy day. | First 200 subs. |
| **Fri May 22** | Essay #1 ships: *"What we ripped out of 30 startups in Q1 2026."* | First send. Target 1K reads. |
| **Wed May 27** | First Receipts post (mid-week, X-only). | Funnel-top trial. |
| **Fri May 29** | Essay #2: *"Cloudflare Workers AI vs OpenAI vs Groq — three months of bills."* | HN-bait piece. |
| **Tue Jun 9** | ProductHunt launch (anchored on Stack Mirror, not newsletter). | Top-5 day finish target. |
| **Fri Jun 12** | Essay #3: *"6 AI sales-agent tools, real inbox, one week."* | Conversion-bait piece. |
| **Tue Jun 16** | First HN submission attempt (essay #2). | Front-page or data. |
| **Fri Jun 19** | Essay #4: *"Razorpay + Stripe + Cashfree for Indian SaaS."* | India vertical signal. |
| **Tue Jul 1** | Stack Mirror v0 ships at `/stack`. First public diff post. | The moat artifact debuts. |
| **Mon Jul 13** | First sponsor cold-outreach campaign (5 vendors). | First yes target by Aug 1. |
| **Fri Aug 1** | Paid tier opens. First 50 paying members target. Premium one-off teardown launches as $49 PDF. | First paywall live. |
| **Fri Aug 8** | M3 revenue checkpoint: ≥$3K MRR or fold the venture. | Decision day. |

---

## 10. What I'm refusing to do

- ❌ Build email sending infrastructure before having 2,500 subscribers. (Phase 2 trigger.)
- ❌ Build a member portal in Phase 1. (Beehiiv handles paid subs natively.)
- ❌ Build the Showcase before Phase 3. (Trust capital must be banked first; selling vendor placement before establishing editorial spine destroys the thesis.)
- ❌ Open community / Discord / Circle in Phase 1 or 2. (Empty rooms kill brands.)
- ❌ Take any Spotlight sponsor where the vendor controls verdict. (Single inviolable rule.)
- ❌ Run paid acquisition before $3K MRR. (Pre-revenue solo doesn't buy attention.)

---

## 11. Open questions for you to decide before launch

1. **India-first framing or global-default-with-India-issues?** I lean global-default-with-quarterly-India-vertical-issues. Cleaner brand, doesn't cap TAM.
2. **Founder tier — open in P1 ($1,500/yr DM access) or wait until P2?** I lean P2. P1 is about cadence not high-touch.
3. **Will you tweet from `@rakesh1002` or build `@aboutai` from scratch?** Lead with personal in P1, transition to brand handle when paid subs >500.
4. **Do you commit to never running an affiliate link?** I think yes. The trust math doesn't survive even one slip.
5. **Tagline lock-in.** Working tagline: *"30 production AI stacks. One honest teardown a week."* — uses the unfair seat in the strapline so the generic name carries weight. If you don't like it, lock an alternative tonight.

Decide these by EOD May 9. Then ship.

---

*Plan authored 2026-05-08. Companion to `verdict-2026-04-27.md`. Action document — not a strategy memo. Either fold this into how you spend Q3, or kill the venture before it compounds opportunity cost.*
