# aboutai — The Trust Engine of the AI Economy

> The definitive source of truth for the AI economy: Verified tools, investigative news, and cohort-based learning.

```
┌─────────────────────────────────────────────────────────────────┐
│                         aboutai                                  │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │   TRUST     │  │    NEWS     │  │   LEARN     │            │
│   │   ENGINE    │  │   & Intel   │  │   Cohorts   │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   Agentic Vetting  │  Hype Meter   │  Live Courses             │
│   Wrapper Detect   │  Verticals    │  Certifications           │
│   Trust Scores     │  Daily Brief  │  Community                │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Mission

Move beyond "discovery" to **verification**. While incumbents list 5,000+ tools with no quality control, aboutai uses autonomous AI agents to test, score, and expose "wrapper" applications—becoming the arbiter of truth in a market flooded with noise.

## 📁 Repository Structure

```
aboutai/
├── apps/                    # Next.js frontend application
│   ├── app/                 # App router pages
│   ├── components/          # React components
│   ├── content/             # MDX content (news, listings)
│   │   ├── news/            # News articles (MDX)
│   │   ├── tools/           # Tool listings (MDX)
│   │   └── learn/           # Learning content
│   ├── lib/                 # Utilities and helpers
│   └── public/              # Static assets
│
├── docs/                    # Documentation
│   ├── architecture/        # System design docs
│   ├── deployment/          # Production deployment guides
│   ├── execution/           # Development execution plan
│   └── launch/              # Launch checklist
│
├── strategy/                # Business & Product Strategy
│   ├── business/            # Business thesis
│   ├── product/             # PRD and specs
│   └── marketing/           # Go-to-market
│
├── packages/                # Shared packages (future)
│   ├── trust-engine/        # Agentic vetting system
│   ├── ui/                  # Shared UI components
│   └── config/              # Shared configurations
│
├── scripts/                 # Automation scripts
│   ├── content/             # Content generation
│   └── deploy/              # Deployment automation
│
└── .github/                 # GitHub workflows
    └── workflows/           # CI/CD pipelines
```

## 🚀 Quick Start

```bash
# Navigate to the apps directory
cd apps

# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

## 🏗️ Core Modules

### 1. Trust Engine (Directory)
- **Agentic Vetting**: Autonomous AI agents test tools
- **Wrapper Detection**: Identify thin API wrappers
- **Trust Score**: Composite score (0-100) based on reliability, transparency, tech depth

### 2. News & Intelligence
- **Hype Meter**: NLP analysis detecting sensationalism
- **Vertical Feeds**: AgTech, Legal, DevTools, Manufacturing
- **Daily Brief**: Automated newsletter generation

### 3. Community & Learning
- **Cohort Courses**: Live, instructor-led programs
- **Certifications**: "aboutai Certified" credentials
- **Inner Circle**: Premium community access

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [System Architecture](./docs/architecture/SYSTEM_ARCHITECTURE.md) | Full technical architecture |
| [Deployment Guide](./docs/deployment/PRODUCTION_DEPLOYMENT.md) | Production deployment steps |
| [Execution Plan](./docs/execution/EXECUTION_PLAN.md) | Development roadmap |
| [Launch Checklist](./docs/launch/LAUNCH_CHECKLIST.md) | Pre-launch verification |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS |
| **Content** | MDX, Contentlayer |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Auth** | Clerk / Supabase Auth |
| **API** | Next.js API Routes + FastAPI (Agents) |
| **Queue** | Redis + BullMQ |
| **Search** | Algolia |
| **Email** | Beehiiv API |
| **Payments** | Stripe |
| **Deploy** | Vercel (Frontend), Railway/Fly.io (Backend) |

## 📊 Key Metrics

- **North Star**: `verified_deployments` — Users adopting tools after viewing Trust Score
- **Leading**: Trust Scores generated, Wrapper detections, Newsletter signups
- **Lagging**: Revenue, Enterprise contracts, Cohort enrollments

## 🗺️ Roadmap

| Phase | Timeline | Focus |
|-------|----------|-------|
| **Phase 1** | Weeks 1-4 | Crawler & Database, Basic Directory |
| **Phase 2** | Weeks 5-8 | MVP Directory, Wrapper Detector, Newsletter |
| **Phase 3** | Weeks 9-12 | Trust Engine, Agentic Testing |
| **Phase 4** | Weeks 13+ | Verticals, Cohorts, Community |

## 📄 License

Proprietary — All rights reserved.

---

<p align="center">
  <strong>aboutai</strong> — Beyond discovery. Into verification.
</p>

