# aboutai Backend

Autonomous content pipeline for the AI Trust Engine. Self-hosted, open source.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTENT PIPELINE (Celery)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   SCRAPER   │────▶│ TRUST ENGINE│────▶│  PUBLISHER  │                   │
│  │   Sources   │     │   Analysis  │     │  MDX Files  │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│        │                   │                   │                            │
│        ▼                   ▼                   ▼                            │
│   • RSS Feeds          • Wrapper Detection  • Generate MDX                  │
│   • GitHub API         • Trust Score Calc   • Frontend Content              │
│   • HackerNews         • Hype Meter         • Auto Publish                  │
│   • SearXNG Search     • Vertical Class.    │                               │
│                                             │                               │
│                                             ▼                               │
│                                   frontend/content/*.mdx                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Self-Hosted Stack

All services are **open source and self-hostable**:

| Service | Purpose | Replaces |
|---------|---------|----------|
| **SearXNG** | Metasearch engine | Algolia |
| **Redis** | Task queue & cache | - |
| **Celery** | Background jobs | - |
| **PostgreSQL** | Database (optional) | Supabase |

## Quick Start

### 1. Environment Setup

```bash
cp env.sample .env
# Edit .env with your OpenAI API key
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| SearXNG | http://localhost:8080 |
| Flower (task monitor) | http://localhost:5555 |

## API Endpoints

### Search

```bash
# Search using self-hosted SearXNG
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI coding assistant", "categories": ["general"]}'
```

### Analyze Tool

```bash
# Analyze a tool for wrapper detection
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://some-ai-tool.com"}'
```

### Pipeline

```bash
# Trigger content pipeline
curl -X POST http://localhost:8000/api/v1/pipeline/run

# Check pipeline status
curl http://localhost:8000/api/v1/pipeline/{pipeline_id}
```

### Drafts

```bash
# List pending drafts
curl http://localhost:8000/api/v1/drafts

# Approve a draft
curl -X POST http://localhost:8000/api/v1/drafts/{draft_id}/approve

# Publish all approved
curl -X POST http://localhost:8000/api/v1/publish
```

## Trust Engine

The Trust Engine analyzes AI tools and calculates a Trust Score (0-100):

```
TrustScore = (0.30 × P_tech) + (0.40 × R_test) + (0.15 × T_trans) + (0.15 × L_life)
```

| Component | Weight | Description |
|-----------|--------|-------------|
| P_tech | 30% | Proprietary technology indicators |
| R_test | 40% | Reliability/testing score |
| T_trans | 15% | Transparency (docs, pricing, team) |
| L_life | 15% | Liveness (activity, updates) |

### Wrapper Classification

| Status | Likelihood | Description |
|--------|------------|-------------|
| native | 0-20% | Custom models, proprietary R&D |
| fine_tuned | 21-40% | Domain-specific fine-tuning |
| rag | 41-60% | Proprietary knowledge bases |
| wrapper | 61-100% | UI layer over foundation APIs |

## Hype Meter

News articles are scored for sensationalism (0-100, lower is better):

**Hype indicators**: "revolutionary", "game-changing", "AGI", "breakthrough"
**Factual indicators**: "benchmark", "study shows", "limitations", "peer-reviewed"

## Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| Full Pipeline | Every 4 hours | Scrape all sources, analyze, create drafts |
| RSS Scrape | Every 2 hours | Parse all RSS feeds |
| GitHub Scrape | Daily 3 AM | Search trending AI repos |
| HackerNews | Every 4 hours | Search AI discussions |
| Publish Approved | Hourly | Publish approved drafts |
| Auto-Approve | Hourly | Approve high-quality drafts |

## Development

### Run locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# Start SearXNG
docker run -d -p 8080:8080 searxng/searxng:latest

# Start API
uvicorn app.main:app --reload

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.core.celery_app beat --loglevel=info
```

### Project Structure

```
app/
├── main.py              # FastAPI application
├── core/
│   ├── config.py        # Settings (Pydantic)
│   └── celery_app.py    # Celery configuration
├── api/
│   └── routes.py        # API endpoints
├── agents/
│   ├── trust_engine.py  # Wrapper detection & scoring
│   └── scraper/
│       └── sources.py   # RSS, GitHub, HN scrapers
├── services/
│   └── publisher.py     # MDX file generation
├── tasks/
│   └── pipeline_tasks.py # Celery tasks
└── models/
    └── __init__.py      # Pydantic models
```

## License

MIT
