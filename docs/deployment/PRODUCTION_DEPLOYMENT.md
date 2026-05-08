# Production Deployment Guide — aboutai

> Complete guide for deploying aboutai to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Database Setup (Supabase)](#database-setup)
4. [Frontend Deployment (Vercel)](#frontend-deployment)
5. [Trust Engine Deployment](#trust-engine-deployment)
6. [Third-Party Service Configuration](#third-party-services)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring & Alerting](#monitoring)
9. [Rollback Procedures](#rollback)

---

## Prerequisites

### Required Accounts

| Service                                                    | Purpose          | Tier Needed    |
| ---------------------------------------------------------- | ---------------- | -------------- |
| [Vercel](https://vercel.com)                               | Frontend hosting | Pro ($20/mo)   |
| [Supabase](https://supabase.com)                           | Database         | Pro ($25/mo)   |
| [Railway](https://railway.app) or [Fly.io](https://fly.io) | Trust Engine     | Starter        |
| [Upstash](https://upstash.com)                             | Redis queue      | Pay-as-you-go  |
| [OpenAI](https://platform.openai.com)                      | LLM API          | API access     |
| [Browserbase](https://browserbase.com)                     | Headless browser | Starter        |
| [Algolia](https://algolia.com)                             | Search           | Free tier ok   |
| [Beehiiv](https://beehiiv.com)                             | Newsletter       | Scale ($99/mo) |
| [Stripe](https://stripe.com)                               | Payments         | Standard       |
| [Clerk](https://clerk.com)                                 | Auth (optional)  | Free tier ok   |

### Local Requirements

```bash
# Required tools
node --version  # >= 20.x
npm --version   # >= 10.x
python --version  # >= 3.11

# Recommended tools
vercel --version
railway --version
supabase --version
```

---

## Infrastructure Setup

### 1. Clone and Configure Repository

```bash
# Clone repository
git clone https://github.com/your-org/aboutai.git
cd aboutai

# Install dependencies
cd apps && npm install

# Copy environment template
cp .env.example .env.local
```

### 2. Environment Variables Template

Create `.env.example` for documentation:

```bash
# ============================================
# ABOUTAI ENVIRONMENT CONFIGURATION
# ============================================

# Application
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://theaidaily.in

# --------------------------------------------
# DATABASE (Supabase)
# --------------------------------------------
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# --------------------------------------------
# AUTHENTICATION (Clerk)
# --------------------------------------------
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
CLERK_WEBHOOK_SECRET=

# --------------------------------------------
# LLM PROVIDERS
# --------------------------------------------
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# --------------------------------------------
# TRUST ENGINE
# --------------------------------------------
TRUST_ENGINE_URL=
TRUST_ENGINE_API_KEY=
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=

# --------------------------------------------
# QUEUE (Upstash Redis)
# --------------------------------------------
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# --------------------------------------------
# SEARCH (Algolia)
# --------------------------------------------
NEXT_PUBLIC_ALGOLIA_APP_ID=
NEXT_PUBLIC_ALGOLIA_SEARCH_KEY=
ALGOLIA_ADMIN_API_KEY=

# --------------------------------------------
# NEWSLETTER (Beehiiv)
# --------------------------------------------
BEEHIIV_API_KEY=
BEEHIIV_PUBLICATION_ID=

# --------------------------------------------
# PAYMENTS (Stripe)
# --------------------------------------------
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# --------------------------------------------
# ANALYTICS
# --------------------------------------------
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=

# --------------------------------------------
# ERROR TRACKING
# --------------------------------------------
SENTRY_DSN=
SENTRY_AUTH_TOKEN=
```

---

## Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) → New Project
2. Choose region closest to your users (e.g., `us-east-1`)
3. Save the project URL and keys

### 2. Run Database Migrations

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Push migrations
supabase db push
```

### 3. Database Schema Migration

Create `supabase/migrations/001_initial_schema.sql`:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Tools table
CREATE TABLE public.tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    logo_url TEXT,

    -- Classification
    vertical TEXT CHECK (vertical IN ('agtech', 'legal', 'devtools', 'marketing', 'general')),
    categories TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Trust Engine
    trust_score INTEGER CHECK (trust_score >= 0 AND trust_score <= 100),
    wrapper_status TEXT CHECK (wrapper_status IN ('native', 'fine_tuned', 'rag', 'wrapper', 'unknown')) DEFAULT 'unknown',
    is_verified BOOLEAN DEFAULT FALSE,

    -- Pricing
    pricing_model JSONB DEFAULT '{}',

    -- Metadata
    featured BOOLEAN DEFAULT FALSE,
    last_audited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit logs
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES public.tools(id) ON DELETE CASCADE,
    agent_version TEXT NOT NULL,
    agent_type TEXT CHECK (agent_type IN ('wrapper', 'functional', 'grader')),
    test_prompt TEXT,
    tool_response TEXT,
    grader_evaluation JSONB,
    hallucination_detected BOOLEAN,
    latency_ms INTEGER,
    reliability_score FLOAT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- News items
CREATE TABLE public.news_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT,
    excerpt TEXT,
    cover_image TEXT,
    vertical TEXT,
    tags TEXT[] DEFAULT '{}',
    hype_score INTEGER CHECK (hype_score >= 0 AND hype_score <= 100),
    source_url TEXT,
    author TEXT,
    status TEXT CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscribers
CREATE TABLE public.subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    verticals TEXT[] DEFAULT '{}',
    beehiiv_id TEXT,
    status TEXT CHECK (status IN ('active', 'unsubscribed')) DEFAULT 'active',
    subscribed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Profiles (linked to auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT,
    avatar_url TEXT,
    tier TEXT CHECK (tier IN ('free', 'pro', 'enterprise')) DEFAULT 'free',
    stripe_customer_id TEXT,
    tools_saved UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tool embeddings for semantic search
CREATE TABLE public.tool_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES public.tools(id) ON DELETE CASCADE,
    embedding vector(1536),
    content_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tools_vertical ON public.tools(vertical);
CREATE INDEX idx_tools_trust_score ON public.tools(trust_score DESC);
CREATE INDEX idx_tools_featured ON public.tools(featured) WHERE featured = TRUE;
CREATE INDEX idx_news_status ON public.news_items(status);
CREATE INDEX idx_news_published_at ON public.news_items(published_at DESC);
CREATE INDEX idx_tool_embeddings_vector ON public.tool_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Row Level Security
ALTER TABLE public.tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Public read access for tools and news
CREATE POLICY "Public tools read" ON public.tools FOR SELECT USING (true);
CREATE POLICY "Public news read" ON public.news_items FOR SELECT USING (status = 'published');

-- Authenticated profile access
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Updated at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tools_updated_at BEFORE UPDATE ON public.tools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER news_updated_at BEFORE UPDATE ON public.news_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 4. Enable Realtime (Optional)

```sql
-- Enable realtime for specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE public.tools;
ALTER PUBLICATION supabase_realtime ADD TABLE public.news_items;
```

---

## Frontend Deployment

### 1. Connect to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link project (from /apps directory)
cd apps
vercel link
```

### 2. Configure Vercel Project

```bash
# Set environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# ... add all other variables

# Or import from file
vercel env pull .env.production.local
```

### 3. Deploy

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

### 4. Domain Configuration

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add `theaidaily.in` and `www.theaidaily.in`
3. Configure DNS:

```
Type    Name    Value
A       @       76.76.21.21
CNAME   www     cname.vercel-dns.com
```

### 5. Vercel Configuration File

Create `apps/vercel.json`:

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "functions": {
    "api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/tools/:slug/",
      "destination": "/tools/:slug",
      "permanent": true
    }
  ]
}
```

---

## Trust Engine Deployment

### Option A: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up
```

Create `trust-engine/railway.json`:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `trust-engine/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option B: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly launch

# Deploy
fly deploy
```

Create `trust-engine/fly.toml`:

```toml
app = "aboutai-trust-engine"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 2
  memory_mb = 1024
```

---

## Third-Party Services

### Algolia Setup

```bash
# Create indexes via API or dashboard
# Index: aboutai_tools
# Index: aboutai_news

# Configure searchable attributes:
# - name
# - description
# - tags
# - vertical
```

Sync script `scripts/sync-algolia.ts`:

```typescript
import { algoliasearch } from "algoliasearch";
import { createClient } from "@supabase/supabase-js";

const algolia = algoliasearch(
  process.env.ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

async function syncTools() {
  const { data: tools } = await supabase.from("tools").select("*");

  const records = tools?.map((tool) => ({
    objectID: tool.id,
    ...tool,
  }));

  await algolia.saveObjects({
    indexName: "aboutai_tools",
    objects: records || [],
  });
}

syncTools();
```

### Beehiiv Integration

Configure webhook in Beehiiv dashboard:

```
Webhook URL: https://theaidaily.in/api/webhooks/beehiiv
Events: subscription.created, subscription.deleted
```

### Stripe Setup

1. Create Products in Stripe Dashboard:

   - `aboutai_pro` - Pro subscription
   - `aboutai_enterprise` - Enterprise subscription
   - `aboutai_audit` - Deep Audit one-time

2. Configure webhooks:

```
Webhook URL: https://theaidaily.in/api/webhooks/stripe
Events:
  - checkout.session.completed
  - customer.subscription.updated
  - customer.subscription.deleted
```

---

## CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: apps/package-lock.json

      - name: Install dependencies
        working-directory: apps
        run: npm ci

      - name: Lint
        working-directory: apps
        run: npm run lint

      - name: Type check
        working-directory: apps
        run: npm run type-check

      - name: Build
        working-directory: apps
        run: npm run build

  deploy-preview:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm install -g vercel@latest

      - name: Pull Vercel Environment
        working-directory: apps
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        working-directory: apps
        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy Preview
        working-directory: apps
        run: vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }}

  deploy-production:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm install -g vercel@latest

      - name: Pull Vercel Environment
        working-directory: apps
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build
        working-directory: apps
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy Production
        working-directory: apps
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Monitoring

### Recommended Stack

| Tool                     | Purpose                          |
| ------------------------ | -------------------------------- |
| **Vercel Analytics**     | Web vitals, traffic              |
| **PostHog**              | Product analytics, feature flags |
| **Sentry**               | Error tracking                   |
| **Better Stack**         | Uptime monitoring                |
| **PlanetScale/Supabase** | Database monitoring              |

### Health Check Endpoint

Create `apps/app/api/health/route.ts`:

```typescript
import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export async function GET() {
  const checks = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    services: {} as Record<string, boolean>,
  };

  // Check Supabase
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
    await supabase.from("tools").select("id").limit(1);
    checks.services.database = true;
  } catch {
    checks.services.database = false;
    checks.status = "degraded";
  }

  return NextResponse.json(checks, {
    status: checks.status === "healthy" ? 200 : 503,
  });
}
```

---

## Rollback Procedures

### Vercel Rollback

```bash
# List deployments
vercel ls

# Promote previous deployment to production
vercel promote [deployment-url]

# Or via dashboard
# Vercel Dashboard → Deployments → ... → Promote to Production
```

### Database Rollback

```bash
# List migrations
supabase migration list

# Create rollback migration
supabase migration new rollback_xyz

# Or restore from backup (Supabase Pro)
# Dashboard → Database → Backups → Restore
```

### Emergency Procedures

1. **Immediate rollback**: Use Vercel's instant rollback
2. **Database issue**: Enable maintenance mode, restore backup
3. **Third-party outage**: Graceful degradation, show cached content
4. **Security incident**: Rotate all API keys, deploy security patch

---

## Post-Deployment Checklist

- [ ] Verify all environment variables are set
- [ ] Test authentication flow
- [ ] Test Stripe payment flow (use test mode)
- [ ] Verify newsletter signup works
- [ ] Test tool submission flow
- [ ] Check Wrapper Detector functionality
- [ ] Verify search works (Algolia)
- [ ] Check error tracking (Sentry)
- [ ] Confirm analytics (PostHog)
- [ ] Test on mobile devices
- [ ] Run Lighthouse audit
- [ ] Verify SSL certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring alerts

---

_Last Updated: November 2025_
