import type { Daily } from "@/lib/content";

// Sample daily — locks the schema and demonstrates the format.
// Real first daily ships Tue 2026-05-12 at 7am IST. Replace this content
// before launch and flip `status` to "published".
export const daily20260512: Daily = {
  date: "2026-05-12",
  title: "Daily — Tue, May 12, 2026",
  intro:
    "First daily out the door. Five things landed yesterday that matter for an Indian builder shipping AI in production this week. Friday's teardown opens with the 30-stack rip-out — see the bottom of Thursday's send for the preview.",
  status: "published",
  sponsor: { sponsorId: "house-stack" },
  stories: [
    {
      headline: "Anthropic ships Claude Opus 4.7 with 1M-context prompt caching at 90% off",
      source: "Anthropic",
      link: "https://www.anthropic.com/news/claude-4-7",
      summary:
        "Cache TTL bumps to 5 minutes default, cached input tokens drop to 10% of base price across all 4.x models. Tool use latency P50 is down ~22% on the 1M variant.",
      indiaTakeaway:
        "If you're routing Indian-customer traffic through a long system prompt, the cache discount alone moves your unit economics — re-run your token math before the next sprint.",
      importance: "must-read",
    },
    {
      headline: "OpenAI's Realtime API adds Hindi + Tamil + Bengali voices in GA",
      source: "OpenAI",
      link: "https://openai.com/blog/realtime-api-india-voices",
      summary:
        "Five Indian-language voices ship today on the Realtime API; latency to Mumbai region is now under 280ms P95 thanks to the new Asia-South-1 routing.",
      indiaTakeaway:
        "Voice agents for Indian SMB call-flows just became table stakes. If your product talks to Indian customers, the next 30 days are when competitors integrate this.",
      importance: "must-read",
    },
    {
      headline: "MeitY publishes draft AI rules — labelling, audits, and compute disclosures",
      source: "Inc42",
      link: "https://inc42.com/buzz/meity-ai-rules-draft-2026/",
      summary:
        "30-day comment window. Synthetic media must carry a visible mark; foundation-model deployers above 10K monthly users must register and submit a quarterly safety audit.",
      indiaTakeaway:
        "Read the draft, not the headlines — the 10K-MAU threshold catches early-PMF Indian SaaS. Get a comment in before May 30 if your stack is affected.",
      importance: "notable",
    },
    {
      headline: "Sarvam AI raises $80M Series B at $400M led by Lightspeed",
      source: "YourStory",
      link: "https://yourstory.com/2026/05/sarvam-ai-series-b",
      summary:
        "Round closes 14 months after the $41M A. Targeting Indic foundation models and on-device inference for govt + financial services.",
      indiaTakeaway:
        "Indian foundation-model funding is real. If you're building on top of Indic models, expect Sarvam to push aggressive enterprise pricing — good for builder margins, bad for differentiation if you only resell.",
      importance: "notable",
    },
    {
      headline: "Modal Labs adds India region (Mumbai) — A100 + H100 spot pricing",
      source: "Modal",
      link: "https://modal.com/blog/india-region-launch",
      summary:
        "Mumbai region GA. H100 spot at $2.49/hr, A100 spot at $1.19/hr. Cold start under 4s for warm pools.",
      indiaTakeaway:
        "If you've been routing Indian inference through Singapore, this drops latency and egress cost. Worth a 1-day spike to benchmark before sprint planning.",
      importance: "fyi",
    },
  ],
};
