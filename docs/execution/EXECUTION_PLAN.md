# Execution Plan — aboutai

> Detailed week-by-week development roadmap for bringing aboutai to production.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEVELOPMENT TIMELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1          PHASE 2          PHASE 3          PHASE 4                │
│  Foundation       MVP Launch       Trust Engine     Scale                   │
│  Weeks 1-4        Weeks 5-8        Weeks 9-12       Weeks 13+              │
│                                                                             │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐            │
│  │ Infra   │      │ Frontend│      │ Agents  │      │ Verticals│           │
│  │ Schema  │  ──▶ │ MDX     │  ──▶ │ Testing │  ──▶ │ Cohorts  │           │
│  │ Content │      │ Launch  │      │ Scores  │      │ Scale    │           │
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Infrastructure & Database

**Goal**: Set up core infrastructure and database schema.

#### Day 1-2: Project Setup
- [ ] Initialize monorepo structure
- [ ] Configure TypeScript, ESLint, Prettier
- [ ] Set up Git hooks (Husky, lint-staged)
- [ ] Create development environment documentation

```bash
# Commands to run
cd apps
npm install -D husky lint-staged prettier
npx husky init
```

#### Day 3-4: Database Setup
- [ ] Create Supabase project
- [ ] Write and test database migrations
- [ ] Set up Row Level Security policies
- [ ] Configure database backups

#### Day 5-7: Authentication & Core APIs
- [ ] Integrate Clerk/Supabase Auth
- [ ] Create base API routes
- [ ] Set up error handling middleware
- [ ] Create health check endpoint

**Deliverables**:
- ✅ Working Supabase database with schema
- ✅ Authentication flow working
- ✅ Base API structure in place

---

### Week 2: Content Architecture (MDX)

**Goal**: Set up MDX-based content system for tools and news.

#### Day 1-2: MDX Configuration
- [ ] Install and configure `@next/mdx`
- [ ] Set up Contentlayer for content processing
- [ ] Create content schemas for tools and news
- [ ] Configure MDX components

```bash
# Dependencies
npm install @next/mdx @mdx-js/loader @mdx-js/react
npm install contentlayer next-contentlayer
```

#### Day 3-4: Content Structure
- [ ] Create `/content/tools/` directory structure
- [ ] Create `/content/news/` directory structure
- [ ] Write sample MDX files for testing
- [ ] Create content templates

#### Day 5-7: Dynamic Routes
- [ ] Build `/tools/[slug]` dynamic route
- [ ] Build `/news/[slug]` dynamic route
- [ ] Create tool listing page
- [ ] Create news listing page

**Deliverables**:
- ✅ MDX content system working
- ✅ Dynamic routes for tools and news
- ✅ Sample content rendering correctly

---

### Week 3: Design System & Core Components

**Goal**: Build reusable UI components and establish design language.

#### Day 1-2: Design Tokens & Theme
- [ ] Define color palette (CSS variables)
- [ ] Set up typography scale
- [ ] Configure Tailwind theme
- [ ] Create dark mode support

#### Day 3-5: Component Library
- [ ] Button, Input, Card components
- [ ] Navigation header and footer
- [ ] Trust Score badge component
- [ ] Tool card component
- [ ] News card component
- [ ] Wrapper status indicator

#### Day 6-7: Layout Components
- [ ] Marketing page layout
- [ ] Platform page layout
- [ ] Tool detail layout
- [ ] News article layout

**Deliverables**:
- ✅ Complete design system
- ✅ Core component library
- ✅ Consistent visual language

---

### Week 4: Data Pipeline & Initial Content

**Goal**: Populate database with initial tools and set up ingestion.

#### Day 1-3: Data Ingestion Scripts
- [ ] Write GitHub trending tools scraper
- [ ] Write Product Hunt scraper
- [ ] Create manual tool submission CLI
- [ ] Build data validation layer

```python
# scripts/ingest_tools.py
import asyncio
from scrapers import GitHubScraper, ProductHuntScraper

async def main():
    github = GitHubScraper()
    ph = ProductHuntScraper()
    
    tools = await asyncio.gather(
        github.get_trending_ai_tools(limit=100),
        ph.get_ai_tools(limit=100)
    )
    
    # Deduplicate and validate
    # Insert into Supabase
```

#### Day 4-5: Content Population
- [ ] Ingest top 100 AI tools
- [ ] Write 10 seed MDX tool listings
- [ ] Write 5 seed MDX news articles
- [ ] Populate categories and tags

#### Day 6-7: Search Integration
- [ ] Set up Algolia indexes
- [ ] Sync tools to Algolia
- [ ] Build search UI component
- [ ] Test search functionality

**Deliverables**:
- ✅ 100+ tools in database
- ✅ 10 featured tool listings (MDX)
- ✅ 5 news articles
- ✅ Working search

---

## Phase 2: MVP Launch (Weeks 5-8)

### Week 5: Wrapper Detector MVP

**Goal**: Build the signature "Wrapper Detector" feature.

#### Day 1-3: Backend Logic
- [ ] Create wrapper analysis API endpoint
- [ ] Build basic heuristic detection
- [ ] Implement API latency comparison
- [ ] Create response formatting

```typescript
// Basic wrapper detection heuristics
interface WrapperAnalysis {
  isLikelyWrapper: boolean;
  confidence: number;
  signals: {
    directApiDependency: boolean;
    hasVectorDB: boolean;
    hasFineTuning: boolean;
    disclosesModel: boolean;
  };
  label: 'native' | 'fine_tuned' | 'rag' | 'wrapper';
}
```

#### Day 4-5: Frontend UI
- [ ] Build URL input component
- [ ] Create loading/analyzing states
- [ ] Design results "nutrition label" UI
- [ ] Add share functionality

#### Day 6-7: Polish & Testing
- [ ] Rate limiting implementation
- [ ] Error handling
- [ ] Analytics tracking
- [ ] End-to-end testing

**Deliverables**:
- ✅ Working Wrapper Detector on homepage
- ✅ API endpoint for analysis
- ✅ Beautiful results display

---

### Week 6: Directory & Tool Pages

**Goal**: Complete tool directory and individual tool pages.

#### Day 1-2: Directory Page
- [ ] Category filters
- [ ] Trust Score sorting
- [ ] Pagination
- [ ] Grid/list view toggle

#### Day 3-4: Tool Detail Pages
- [ ] Hero section with logo, name, Trust Score
- [ ] Description and features (from MDX)
- [ ] Pricing information
- [ ] "Audit Logs" evidence section
- [ ] Related tools sidebar

#### Day 5-7: Interactivity
- [ ] "Save to collection" (authenticated)
- [ ] Tool comparison feature
- [ ] Share functionality
- [ ] Report/flag feature

**Deliverables**:
- ✅ Complete directory with filters
- ✅ Rich tool detail pages
- ✅ User interactions working

---

### Week 7: Newsletter & Marketing

**Goal**: Launch newsletter and marketing pages.

#### Day 1-2: Beehiiv Integration
- [ ] Newsletter signup form
- [ ] Beehiiv API integration
- [ ] Vertical selection (AgTech, Legal, etc.)
- [ ] Welcome email automation

#### Day 3-4: Marketing Pages
- [ ] Homepage redesign
- [ ] About page
- [ ] Pricing page (future features)
- [ ] "Manifesto" blog post

#### Day 5-7: SEO & Analytics
- [ ] Meta tags and Open Graph
- [ ] Sitemap generation
- [ ] robots.txt configuration
- [ ] PostHog/Analytics setup

**Deliverables**:
- ✅ Newsletter signup working
- ✅ Marketing pages complete
- ✅ SEO foundation in place

---

### Week 8: Soft Launch & Feedback

**Goal**: Soft launch to beta users, gather feedback.

#### Day 1-2: Pre-launch Checklist
- [ ] Security audit
- [ ] Performance testing
- [ ] Mobile responsiveness check
- [ ] Cross-browser testing

#### Day 3-4: Beta Launch
- [ ] Deploy to production
- [ ] Invite 50 beta users
- [ ] Set up feedback collection (Canny/Typeform)
- [ ] Monitor error logs

#### Day 5-7: Iteration
- [ ] Collect and categorize feedback
- [ ] Fix critical bugs
- [ ] Prioritize improvements
- [ ] Plan Phase 3

**Deliverables**:
- ✅ Production deployment
- ✅ 50 beta users onboarded
- ✅ Feedback collection system

---

## Phase 3: Trust Engine (Weeks 9-12)

### Week 9: Agentic Infrastructure

**Goal**: Set up infrastructure for AI agents.

#### Day 1-2: Queue System
- [ ] Configure Upstash Redis
- [ ] Set up BullMQ job queues
- [ ] Create job types and handlers
- [ ] Build admin queue dashboard

#### Day 3-5: Agent Framework
- [ ] Install LangChain/LangGraph
- [ ] Create base agent class
- [ ] Build Browserbase integration
- [ ] Set up LLM clients (OpenAI/Anthropic)

#### Day 6-7: Testing Framework
- [ ] Unit tests for agents
- [ ] Mock LLM responses for testing
- [ ] Integration test suite
- [ ] CI/CD for agent tests

**Deliverables**:
- ✅ Queue system operational
- ✅ Agent framework ready
- ✅ Browserbase integration working

---

### Week 10: Functional Testing Agent

**Goal**: Build agent that tests tools and grades outputs.

#### Day 1-3: Tester Agent
- [ ] Tool interaction via browser automation
- [ ] Standard test prompts by category
- [ ] Response capture and logging
- [ ] Latency measurement

```python
class FunctionalTesterAgent:
    async def test_tool(self, tool: Tool) -> TestResult:
        # Navigate to tool
        await self.browser.goto(tool.url)
        
        # Find and interact with main input
        await self.find_and_test_input()
        
        # Capture response
        response = await self.capture_output()
        
        # Log to database
        await self.log_test(tool.id, response)
        
        return TestResult(
            success=bool(response),
            response=response,
            latency_ms=self.latency,
        )
```

#### Day 4-5: Grader Agent
- [ ] Hallucination detection
- [ ] Quality scoring rubric
- [ ] Comparative analysis
- [ ] Evidence collection

#### Day 6-7: Integration
- [ ] Connect tester → grader pipeline
- [ ] Store results in audit_logs
- [ ] Surface results on tool pages
- [ ] Manual trigger for testing

**Deliverables**:
- ✅ Functional testing agent
- ✅ Grading agent
- ✅ Results visible on tool pages

---

### Week 11: Trust Score Calculation

**Goal**: Implement complete Trust Score algorithm.

#### Day 1-2: Score Components
- [ ] Proprietary Tech Score calculation
- [ ] Reliability Score from tests
- [ ] Transparency Score analysis
- [ ] Liveness Score (GitHub activity, etc.)

#### Day 3-4: Score Engine
- [ ] Weighted average calculation
- [ ] Score history tracking
- [ ] Score change notifications
- [ ] Batch recalculation system

#### Day 5-7: Display & Badges
- [ ] Trust Score badge designs
- [ ] Score breakdown UI
- [ ] Historical score chart
- [ ] "Verified" badge system

**Deliverables**:
- ✅ Complete Trust Score system
- ✅ Scores displayed on all tools
- ✅ Evidence/audit logs accessible

---

### Week 12: Automation & Monitoring

**Goal**: Automate vetting and set up monitoring.

#### Day 1-3: Scheduled Jobs
- [ ] Daily new tool ingestion
- [ ] Weekly score recalculation
- [ ] Monthly full re-audit
- [ ] "Zombie" tool detection (abandoned tools)

#### Day 4-5: Admin Dashboard
- [ ] Queue monitoring
- [ ] Manual audit triggers
- [ ] Tool moderation interface
- [ ] Score override capability

#### Day 6-7: Public Launch
- [ ] Remove beta gates
- [ ] Public announcement
- [ ] ProductHunt launch preparation
- [ ] Press outreach

**Deliverables**:
- ✅ Fully automated vetting pipeline
- ✅ Admin dashboard
- ✅ Public launch

---

## Phase 4: Scale (Weeks 13+)

### Weeks 13-14: Vertical Expansion

- [ ] Launch AgTech vertical
- [ ] Launch Legal vertical
- [ ] Vertical-specific newsletters
- [ ] Industry-specific Trust Score adjustments

### Weeks 15-16: Community & Education

- [ ] Circle.so community setup
- [ ] First cohort course design
- [ ] Instructor recruitment
- [ ] Certification program design

### Weeks 17-20: Monetization

- [ ] Verified Listing program
- [ ] Pro subscription tier
- [ ] Enterprise data API
- [ ] Job board launch

---

## Key Milestones

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| **Database Ready** | End Week 1 | Schema deployed, migrations running |
| **MDX Content System** | End Week 2 | Tools and news rendering from MDX |
| **Design System** | End Week 3 | Component library complete |
| **Initial Data** | End Week 4 | 100+ tools, search working |
| **Wrapper Detector** | End Week 5 | Public tool on homepage |
| **Directory MVP** | End Week 6 | Browsable tool directory |
| **Newsletter Live** | End Week 7 | Signups working, first send |
| **Beta Launch** | End Week 8 | 50 users, feedback flowing |
| **Trust Engine V1** | End Week 11 | Trust Scores on all tools |
| **Public Launch** | End Week 12 | Open to public, PR campaign |

---

## Resource Requirements

### Team

| Role | Allocation | Responsibilities |
|------|------------|------------------|
| **Full-stack Dev** | 100% | Frontend, API, integrations |
| **AI/ML Engineer** | 50% | Trust Engine agents |
| **Designer** | 25% | UI/UX, marketing assets |
| **Content** | 25% | MDX articles, tool descriptions |

### Infrastructure Costs (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| Vercel Pro | $20 | Frontend hosting |
| Supabase Pro | $25 | Database |
| Railway | $20 | Trust Engine |
| Upstash | $10 | Redis queue |
| OpenAI | $50-200 | Agent LLM calls |
| Browserbase | $50 | Headless browser |
| Algolia | $0-35 | Search (free tier initially) |
| **Total** | ~$175-360/mo | |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM costs spike | Rate limiting, caching, model fallbacks |
| Tool testing breaks | Graceful degradation, manual override |
| Spam submissions | Captcha, rate limits, manual review queue |
| SEO competition | Unique Trust Score content, backlink strategy |
| Legal (scraping) | Respect robots.txt, focus on public APIs |

---

*Last Updated: November 2025*

