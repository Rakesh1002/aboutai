# System Architecture — aboutai

> Comprehensive technical architecture for the aboutai platform.

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [Frontend Architecture](#frontend-architecture)
3. [Backend Services](#backend-services)
4. [Autonomous Content Pipeline](#autonomous-content-pipeline)
5. [Trust Engine (Agentic Vetting)](#trust-engine)
6. [Data Layer](#data-layer)
7. [Third-Party Integrations](#third-party-integrations)
8. [Infrastructure](#infrastructure)
9. [Security](#security)

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ABOUTAI PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (Vercel)                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │   │
│  │  │  Directory  │ │    News     │ │   Learn     │ │   Wrapper   │    │   │
│  │  │   /tools    │ │   /news     │ │  /courses   │ │  /analyze   │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │   │
│  │                                                                      │   │
│  │  Next.js 16 (App Router) + React 19 + MDX + Tailwind                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     AUTONOMOUS BACKEND (FastAPI)                     │   │
│  │  ┌───────────────────────┐  ┌───────────────────────┐               │   │
│  │  │   Content Orchestrator │  │   Trust Engine        │               │   │
│  │  │   (LangGraph Pipeline) │  │   (Wrapper Detection) │               │   │
│  │  └───────────────────────┘  └───────────────────────┘               │   │
│  │                                                                      │   │
│  │  Multi-Agent System: Researcher → Writer → Enricher → Publisher     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA LAYER                                   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │   │
│  │  │  Supabase   │ │   Redis     │ │   SearXNG   │ │   S3/R2     │    │   │
│  │  │ PostgreSQL  │ │   Queue     │ │   Search    │ │   Assets    │    │   │
│  │  │  + pgvector │ │  (Celery)   │ │ (Self-Host) │ │             │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Technology Stack

| Technology   | Purpose            | Version           |
| ------------ | ------------------ | ----------------- |
| Next.js      | Framework          | 16.x (App Router) |
| React        | UI Library         | 19.x              |
| TypeScript   | Type Safety        | 5.x               |
| Tailwind CSS | Styling            | 4.x               |
| MDX          | Content            | 3.x               |
| Contentlayer | Content Processing | 0.3.x             |

### Directory Structure

```
apps/frontend/
├── app/                          # Next.js App Router
│   ├── (marketing)/              # Marketing pages group
│   │   ├── page.tsx              # Homepage
│   │   ├── about/                # About page
│   │   └── pricing/              # Pricing page
│   │
│   ├── (platform)/               # Platform pages group
│   │   ├── tools/                # Tool directory
│   │   │   ├── page.tsx          # Directory listing
│   │   │   ├── [slug]/           # Individual tool page
│   │   │   └── categories/       # Category pages
│   │   │
│   │   ├── news/                 # News section
│   │   │   ├── page.tsx          # News listing
│   │   │   ├── [slug]/           # Individual article
│   │   │   └── verticals/        # Vertical-specific news
│   │   │
│   │   ├── learn/                # Learning platform
│   │   │   ├── page.tsx          # Course catalog
│   │   │   ├── courses/          # Course pages
│   │   │   └── certifications/   # Certification info
│   │   │
│   │   └── analyze/              # Wrapper Detector
│   │       └── page.tsx          # Analysis tool
│   │
│   ├── api/                      # API routes
│   │   ├── tools/                # Tool CRUD
│   │   ├── analyze/              # Wrapper analysis
│   │   ├── newsletter/           # Newsletter signup
│   │   └── webhooks/             # External webhooks
│   │
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
│
├── components/                   # React components
│   ├── ui/                       # Primitive UI components
│   ├── layout/                   # Layout components
│   ├── tools/                    # Tool-specific components
│   ├── news/                     # News components
│   └── marketing/                # Marketing components
│
├── content/                      # MDX content (auto-generated)
│   ├── news/                     # News articles
│   ├── tools/                    # Tool listings
│   └── learn/                    # Learning content
│
├── lib/                          # Utilities
│   ├── supabase/                 # Supabase client
│   ├── mdx/                      # MDX utilities
│   ├── utils/                    # General utilities
│   └── hooks/                    # Custom React hooks
│
└── public/                       # Static assets
```

### Page Routes

| Route                          | Description                    | Priority |
| ------------------------------ | ------------------------------ | -------- |
| `/`                            | Homepage with Wrapper Detector | P0       |
| `/tools`                       | Tool directory listing         | P0       |
| `/tools/[slug]`                | Individual tool page           | P0       |
| `/tools/categories/[category]` | Category listing               | P1       |
| `/news`                        | News listing                   | P1       |
| `/news/[slug]`                 | Individual article             | P1       |
| `/news/verticals/[vertical]`   | Vertical-specific news         | P2       |
| `/learn`                       | Course catalog                 | P2       |
| `/analyze`                     | Wrapper Detector standalone    | P0       |
| `/about`                       | About page                     | P1       |
| `/pricing`                     | Pricing page                   | P1       |

---

## Backend Services

### Python Backend (FastAPI)

The backend handles autonomous content generation and trust analysis:

```
apps/backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py           # Settings (Pydantic)
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── redis.py            # Redis client
│   │   └── logging.py          # Structured logging
│   │
│   ├── api/
│   │   └── routes.py           # API endpoints
│   │
│   ├── agents/                 # Autonomous agents
│   │   ├── orchestrator.py     # Pipeline coordinator (LangGraph)
│   │   ├── scraper/            # Research & scraping
│   │   │   ├── researcher.py   # SearXNG + web scraping
│   │   │   ├── browser.py      # Playwright automation
│   │   │   └── sources.py      # Source definitions
│   │   ├── writer.py           # Content generation
│   │   ├── enricher.py         # Trust analysis & classification
│   │   ├── citation.py         # Source validation
│   │   ├── formatter.py        # MDX formatting
│   │   └── rewriter.py         # Quality assurance
│   │
│   ├── services/
│   │   ├── search.py           # SearXNG search service
│   │   ├── content.py          # Content management
│   │   ├── publisher.py        # MDX file publishing
│   │   └── newsletter.py       # Newsletter generation
│   │
│   ├── tasks/                  # Celery tasks
│   │   ├── scraper_tasks.py    # Scheduled scraping
│   │   ├── pipeline_tasks.py   # Content pipeline
│   │   └── content_tasks.py    # Publishing tasks
│   │
│   └── models/
│       └── content.py          # Pydantic models
│
├── docker-compose.yml          # All services
├── Dockerfile                  # API container
├── searxng/
│   └── settings.yml            # SearXNG configuration
└── requirements.txt            # Python dependencies
```

---

## Autonomous Content Pipeline

### Multi-Agent Architecture

The content pipeline uses LangGraph to orchestrate multiple specialized agents:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTENT ORCHESTRATOR (LangGraph)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │ RESEARCHER  │────▶│   WRITER    │────▶│  ENRICHER   │                   │
│  │    Agent    │     │    Agent    │     │    Agent    │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│        │                   │                   │                            │
│        ▼                   ▼                   ▼                            │
│   • SearXNG Search     • LLM Content       • Wrapper Detection             │
│   • Playwright Scrape  • Structure Gen     • Trust Score Calc              │
│   • RSS Aggregation    • Editorial Voice   • Vertical Classification       │
│   • API Scraping       • Fact Integration  • Metadata Enrichment           │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  CITATION   │────▶│  FORMATTER  │────▶│  REWRITER   │                   │
│  │   Manager   │     │    Agent    │     │    Agent    │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│        │                   │                   │                            │
│        ▼                   ▼                   ▼                            │
│   • URL Validation     • MDX Generation    • Quality Scoring               │
│   • Metadata Extract   • Frontmatter       • Grammar/Style                 │
│   • Attribution        • Section Structure • aboutai Voice                 │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│                    ┌─────────────────┐                                      │
│                    │    PUBLISHER    │                                      │
│                    │    Service      │                                      │
│                    └─────────────────┘                                      │
│                              │                                              │
│                              ▼                                              │
│                    frontend/content/*.mdx                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Descriptions

| Agent          | Purpose                         | Key Technologies               |
| -------------- | ------------------------------- | ------------------------------ |
| **Researcher** | Gathers raw content from web    | SearXNG, Playwright, RSS, APIs |
| **Writer**     | Generates structured content    | GPT-4, Prompt Engineering      |
| **Enricher**   | Analyzes trust & classification | Wrapper Detection, Scoring     |
| **Citation**   | Validates & formats sources     | HTTP validation, metadata      |
| **Formatter**  | Converts to MDX structure       | YAML frontmatter, Markdown     |
| **Rewriter**   | Quality assurance               | Style editing, QA scoring      |

### Scheduled Tasks

| Task                       | Schedule      | Description                    |
| -------------------------- | ------------- | ------------------------------ |
| `scrape_all_sources`       | Every 4 hours | Scrape RSS, news, directories  |
| `refresh_tool_directory`   | Daily 2 AM    | Re-analyze all existing tools  |
| `update_all_trust_scores`  | Every 6 hours | Update trust scores            |
| `publish_approved_content` | Hourly        | Publish approved drafts to MDX |

### Data Sources

**News Sources:**

- TechCrunch AI, VentureBeat AI, The Verge AI
- MIT Technology Review, Ars Technica
- Reddit (r/MachineLearning, r/artificial)
- HackerNews (AI-filtered)
- arXiv AI papers

**Tool Directories:**

- Product Hunt AI
- There's An AI For That
- Future Tools
- TopAI.tools

---

## Trust Engine

### Trust Score Algorithm

$$TrustScore = (w_1 \cdot P_{tech}) + (w_2 \cdot R_{test}) + (w_3 \cdot T_{trans}) + (w_4 \cdot L_{life})$$

| Component   | Weight | Description            |
| ----------- | ------ | ---------------------- |
| $P_{tech}$  | 0.30   | Proprietary Tech Score |
| $R_{test}$  | 0.40   | Reliability Score      |
| $T_{trans}$ | 0.15   | Transparency Score     |
| $L_{life}$  | 0.15   | Liveness Score         |

### Wrapper Detection

```python
class WrapperDetector:
    """
    Analyzes if an AI tool is a thin wrapper over foundation APIs.

    Classification:
    - Native AI (0-20% wrapper): Custom models, proprietary R&D
    - Fine-Tuned (21-40%): Domain-specific fine-tuning
    - RAG-Enhanced (41-60%): Proprietary knowledge bases
    - Light Wrapper (61-80%): Meaningful UX over APIs
    - Pure Wrapper (81-100%): Simple UI over GPT/Claude
    """

    def analyze(self, tool_url: str) -> WrapperAnalysis:
        signals = {
            "has_custom_model": self.detect_custom_model(),
            "has_proprietary_data": self.detect_proprietary_data(),
            "has_unique_features": self.detect_unique_features(),
            "has_enterprise_features": self.detect_enterprise(),
            "sustainable_pricing": self.check_pricing(),
        }

        wrapper_likelihood = self.calculate_likelihood(signals)

        return WrapperAnalysis(
            wrapper_status=self.get_status(wrapper_likelihood),
            confidence=wrapper_likelihood,
            signals=signals,
            reasoning=self.generate_reasoning(signals)
        )
```

---

## Data Layer

### Database Schema (Supabase/PostgreSQL)

```sql
-- Core tool listing
CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    logo_url TEXT,

    -- Classification
    vertical TEXT CHECK (vertical IN ('agtech', 'legal', 'devtools', 'marketing', 'general')),
    categories TEXT[],
    tags TEXT[],

    -- Trust Engine Data
    trust_score INTEGER CHECK (trust_score >= 0 AND trust_score <= 100),
    wrapper_status TEXT CHECK (wrapper_status IN ('native', 'fine_tuned', 'rag', 'wrapper', 'unknown')),
    is_verified BOOLEAN DEFAULT FALSE,

    -- Pricing
    pricing_model JSONB,

    -- Metadata
    last_audited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- News articles
CREATE TABLE news_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,

    -- Classification
    vertical TEXT,
    tags TEXT[],
    hype_score INTEGER CHECK (hype_score >= 0 AND hype_score <= 100),

    -- Source
    source_url TEXT,
    author TEXT,

    -- Pipeline tracking
    pipeline_id TEXT,
    citations JSONB,

    -- Status
    status TEXT CHECK (status IN ('draft', 'pending_review', 'approved', 'published', 'archived')),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content drafts (pending review)
CREATE TABLE content_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type TEXT CHECK (content_type IN ('tool', 'news')),

    -- Generated content
    title TEXT,
    slug TEXT,
    mdx_content TEXT,

    -- Pipeline metadata
    pipeline_id TEXT,
    quality_score FLOAT,

    -- Review status
    status TEXT CHECK (status IN ('draft', 'pending_review', 'approved', 'rejected', 'published')),
    reviewer_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Search (SearXNG — Self-Hosted)

Instead of Algolia, we use **SearXNG** for self-hosted metasearch:

```yaml
# searxng/settings.yml
use_default_settings: true

general:
  instance_name: "aboutai Search"

search:
  safe_search: 0
  autocomplete: "google"
  formats: [html, json]

engines:
  # General Web
  - name: google
    engine: google
    disabled: false
  - name: bing
    engine: bing
    disabled: false
  - name: duckduckgo
    engine: duckduckgo
    disabled: false

  # News
  - name: google news
    engine: google_news
    disabled: false
  - name: bing news
    engine: bing_news
    disabled: false

  # Tech
  - name: github
    engine: github
    disabled: false
  - name: hacker news
    engine: hackernews
    disabled: false
```

**Benefits over Algolia:**

- **Self-hosted**: No vendor lock-in
- **Privacy**: No data sent to third parties
- **Multi-source**: Aggregates 15+ search engines
- **Free**: No per-search costs
- **Customizable**: Full control over engines and filters

---

## Third-Party Integrations

### Required Services

| Service       | Purpose                 | Environment Variables                                       |
| ------------- | ----------------------- | ----------------------------------------------------------- |
| **Supabase**  | Database, Auth, Storage | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` |
| **OpenAI**    | LLM for agents          | `OPENAI_API_KEY`                                            |
| **Anthropic** | Backup LLM              | `ANTHROPIC_API_KEY`                                         |
| **Redis**     | Task queue (Celery)     | `REDIS_URL`                                                 |
| **SearXNG**   | Self-hosted search      | `SEARXNG_URL` (localhost:8080)                              |
| **Beehiiv**   | Newsletter              | `BEEHIIV_API_KEY`, `BEEHIIV_PUBLICATION_ID`                 |
| **Stripe**    | Payments                | `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`               |

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Beehiiv   │  │   Stripe    │  │   SearXNG   │             │
│  │  Newsletter │  │  Payments   │  │   Search    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ABOUTAI BACKEND                       │   │
│  │                                                          │   │
│  │  Newsletter Sync ◄── Beehiiv API                         │   │
│  │  Payments ◄── Stripe webhooks                            │   │
│  │  Search ◄── SearXNG JSON API (self-hosted)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Supabase   │  │ Playwright  │  │   OpenAI    │             │
│  │  Database   │  │   Browser   │  │     LLM     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                      CDN (Vercel Edge)                  │    │
│  │                     Global Distribution                 │    │
│  └─────────────────────────┬──────────────────────────────┘    │
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                 VERCEL (Frontend)                       │    │
│  │                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │    │
│  │  │    SSR      │  │    ISR      │  │   Static    │     │    │
│  │  │   Pages     │  │   Pages     │  │   MDX       │     │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │    │
│  └─────────────────────────┬──────────────────────────────┘    │
│                            │                                    │
│              ┌─────────────┴─────────────┐                     │
│              ▼                           ▼                     │
│  ┌────────────────────┐    ┌────────────────────┐              │
│  │   RAILWAY/FLY.IO   │    │      SUPABASE      │              │
│  │   (Python Backend) │    │    (Database)      │              │
│  │                    │    │                    │              │
│  │  ┌──────────────┐  │    │  ┌──────────────┐  │              │
│  │  │   FastAPI    │  │    │  │  PostgreSQL  │  │              │
│  │  │   + Celery   │  │    │  │   + pgvector │  │              │
│  │  └──────────────┘  │    │  └──────────────┘  │              │
│  │                    │    │                    │              │
│  │  ┌──────────────┐  │    │  ┌──────────────┐  │              │
│  │  │   SearXNG    │  │    │  │   Storage    │  │              │
│  │  │   (Search)   │  │    │  │   (S3)       │  │              │
│  │  └──────────────┘  │    │  └──────────────┘  │              │
│  │                    │    │                    │              │
│  │  ┌──────────────┐  │    └────────────────────┘              │
│  │  │    Redis     │  │                                        │
│  │  │   (Queue)    │  │                                        │
│  │  └──────────────┘  │                                        │
│  └────────────────────┘                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Services

```yaml
# apps/backend/docker-compose.yml
services:
  searxng: # Self-hosted metasearch
  redis: # Task queue
  api: # FastAPI backend
  celery-worker: # Background tasks
  celery-beat: # Scheduler
  flower: # Task monitoring
```

---

## Security

### Security Measures

| Area               | Implementation                                 |
| ------------------ | ---------------------------------------------- |
| **Authentication** | Supabase Auth with JWT                         |
| **API Security**   | Rate limiting, API key rotation                |
| **Database**       | Row Level Security (RLS) in Supabase           |
| **Secrets**        | Environment variables, Vercel/Railway secrets  |
| **CORS**           | Strict origin policies                         |
| **Content**        | CSP headers, sanitized MDX                     |
| **Payments**       | Stripe webhooks with signature verification    |
| **Search**         | Self-hosted SearXNG (no data to third parties) |

### Rate Limiting

```typescript
const RATE_LIMITS = {
  anonymous: { requests: 5, window: "1h" },
  authenticated: { requests: 50, window: "1h" },
  pro: { requests: 500, window: "1h" },
  enterprise: { requests: Infinity, window: "1h" },
};
```

---

## Performance Targets

| Metric           | Target  | Measurement        |
| ---------------- | ------- | ------------------ |
| **LCP**          | < 2.5s  | Core Web Vitals    |
| **FID**          | < 100ms | Core Web Vitals    |
| **CLS**          | < 0.1   | Core Web Vitals    |
| **TTFB**         | < 200ms | Server response    |
| **API p95**      | < 500ms | API latency        |
| **Trust Engine** | < 30s   | Full analysis time |
| **Pipeline**     | < 5min  | Full content gen   |

---

_Last Updated: November 2025_
