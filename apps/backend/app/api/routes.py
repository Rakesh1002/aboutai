"""
API Routes for aboutAI Backend
All endpoints for tools, news, newsletters, podcasts, and admin.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog

from app.services.newsletter import NewsletterService
from app.services.database import (
    DatabaseService,
    get_tools_repo,
    get_news_repo,
    get_submissions_repo,
    get_subscribers_repo,
    ToolsRepository,
    NewsRepository,
    SubmissionsRepository,
    SubscribersRepository,
)
from app.agents.scraper.launch_sites import LaunchSiteAggregator
from app.agents.scraper.podcasts import PodcastAggregator

logger = structlog.get_logger()
router = APIRouter()


def get_db_configured() -> bool:
    """Check if database is configured."""
    return DatabaseService.is_configured()


# =============================================
# Request/Response Models
# =============================================

class ToolSubmissionRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the AI tool to submit")
    submitter_email: Optional[EmailStr] = Field(None, description="Email for notifications")
    notes: Optional[str] = Field(None, max_length=1000)


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr
    source: str = "website"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    category: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)


class ContentApprovalRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|regenerate)$")
    feedback: Optional[str] = None


class PipelineTriggerRequest(BaseModel):
    content_type: str = Field(..., pattern="^(tool|news|both)$")
    query: Optional[str] = None
    url: Optional[HttpUrl] = None


# =============================================
# Tool Submission & Discovery
# =============================================

@router.post("/tools/submit", tags=["Tools"])
async def submit_tool(request: ToolSubmissionRequest, background_tasks: BackgroundTasks):
    """
    Submit a new AI tool for review and listing.
    The tool will be automatically analyzed and content generated.
    """
    logger.info("Tool submission received", url=str(request.url))
    
    try:
        submission_id = None
        
        # Save to database if configured
        if DatabaseService.is_configured():
            submissions_repo = get_submissions_repo()
            submission = await submissions_repo.create({
                "url": str(request.url),
                "submitter_email": request.submitter_email,
                "notes": request.notes,
                "status": "pending",
            })
            submission_id = submission.get("id") if submission else None
        
        # Queue for processing
        from app.tasks.pipeline_tasks import process_single_tool_url
        task = process_single_tool_url.delay(
            str(request.url),
            submitter_email=request.submitter_email,
            notes=request.notes,
            submission_id=submission_id,
        )
        
        return {
            "status": "queued",
            "message": "Tool submitted successfully. We'll review and list it within 24-48 hours.",
            "submission_id": submission_id or task.id,
            "url": str(request.url),
        }
    except Exception as e:
        logger.error("Failed to queue tool submission", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process submission")


@router.get("/tools", tags=["Tools"])
async def list_tools(
    category: Optional[str] = None,
    vertical: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List approved AI tools from the directory.
    """
    if not DatabaseService.is_configured():
        return {"count": 0, "tools": [], "message": "Database not configured"}
    
    try:
        tools_repo = get_tools_repo()
        tools = await tools_repo.list_tools(
            status="approved",
            category=category,
            vertical=vertical,
            limit=limit,
            offset=offset,
        )
        
        return {
            "count": len(tools),
            "tools": tools,
        }
    except Exception as e:
        logger.error("Failed to list tools", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list tools")


@router.get("/tools/launches", tags=["Tools"])
async def get_recent_launches(limit: int = Query(50, ge=1, le=100)):
    """
    Get recent AI tool launches from Product Hunt, BetaList, etc.
    """
    try:
        aggregator = LaunchSiteAggregator()
        launches = await aggregator.aggregate_all_launches(limit_per_source=limit // 5)
        
        return {
            "count": len(launches),
            "launches": [
                {
                    "source": l.source,
                    "title": l.title,
                    "url": l.url,
                    "description": l.description,
                    "votes": l.votes,
                    "category": l.category,
                }
                for l in launches[:limit]
            ]
        }
    except Exception as e:
        logger.error("Failed to fetch launches", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch launches")


# =============================================
# Newsletter
# =============================================

@router.post("/newsletter/subscribe", tags=["Newsletter"])
async def subscribe_newsletter(request: NewsletterSubscribeRequest):
    """
    Subscribe to the aboutAI weekly newsletter.
    """
    logger.info("Newsletter subscription", email=request.email)
    
    # Save to database if configured
    if DatabaseService.is_configured():
        try:
            subscribers_repo = get_subscribers_repo()
            await subscribers_repo.create(request.email, request.source)
        except Exception as e:
            logger.warning("Failed to save subscriber to DB", error=str(e))
    
    # Also subscribe via Beehiiv if configured
    service = NewsletterService()
    result = await service.subscribe(request.email, request.source)
    
    if result.get("success"):
        return {
            "status": "subscribed",
            "message": "Welcome! You'll receive our weekly AI digest.",
        }
    else:
        # Still return success to user (might be already subscribed)
        return {
            "status": "processed",
            "message": "Thanks for your interest in aboutAI!",
        }


@router.get("/newsletter/stats", tags=["Newsletter"])
async def get_newsletter_stats():
    """
    Get newsletter statistics (subscriber count, etc.)
    """
    service = NewsletterService()
    count = await service.get_subscriber_count()
    
    return {
        "subscribers": count,
        "frequency": "weekly",
    }


@router.post("/newsletter/generate-digest", tags=["Newsletter", "Admin"])
async def generate_weekly_digest(
    publish: bool = Query(False, description="Create draft in Beehiiv"),
):
    """
    Generate this week's newsletter digest.
    Admin endpoint to manually trigger digest generation.
    """
    # This would normally fetch from database
    # For now, return a placeholder
    service = NewsletterService()
    
    # Example data - would come from real content
    new_tools = [
        {"title": "Claude 3.5", "url": "https://anthropic.com", "category": "AI Assistant", "pricing": "Freemium", "trust_score": 85},
    ]
    top_news = [
        {"title": "OpenAI announces GPT-5", "url": "https://example.com", "source": "TechCrunch", "published_at": "Today"},
    ]
    
    result = await service.create_weekly_digest(
        new_tools=new_tools,
        top_news=top_news,
        podcast_episodes=[],
        publish=publish,
    )
    
    return {
        "status": "generated",
        "subject": result["content"].subject,
        "published": publish,
    }


# =============================================
# Podcasts
# =============================================

@router.get("/podcasts", tags=["Podcasts"])
async def list_podcasts():
    """
    Get all AI podcasts in our directory.
    """
    try:
        aggregator = PodcastAggregator()
        shows = await aggregator.get_all_shows()
        
        return {
            "count": len(shows),
            "shows": [show.to_dict() for show in shows]
        }
    except Exception as e:
        logger.error("Failed to fetch podcasts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch podcasts")


@router.get("/podcasts/episodes", tags=["Podcasts"])
async def get_recent_episodes(limit: int = Query(50, ge=1, le=100)):
    """
    Get recent podcast episodes across all shows.
    """
    try:
        aggregator = PodcastAggregator()
        episodes = await aggregator.get_recent_episodes(limit=limit)
        
        return {
            "count": len(episodes),
            "episodes": [ep.to_dict() for ep in episodes]
        }
    except Exception as e:
        logger.error("Failed to fetch episodes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch episodes")


@router.get("/podcasts/discover", tags=["Podcasts"])
async def discover_podcasts(query: str = Query("artificial intelligence", min_length=2)):
    """
    Discover new AI-related podcasts using iTunes search.
    """
    try:
        aggregator = PodcastAggregator()
        results = await aggregator.discover_new_podcasts(query)
        
        return {
            "count": len(results),
            "podcasts": results
        }
    except Exception as e:
        logger.error("Failed to discover podcasts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to discover podcasts")


# =============================================
# Content Pipeline & Admin
# =============================================

@router.post("/pipeline/trigger", tags=["Admin"])
async def trigger_pipeline(request: PipelineTriggerRequest, background_tasks: BackgroundTasks):
    """
    Manually trigger the content generation pipeline.
    Admin endpoint for on-demand content generation.
    """
    from app.tasks.pipeline_tasks import (
        start_full_content_pipeline,
        process_single_tool_url,
        process_news_query,
    )
    
    logger.info("Pipeline triggered manually", content_type=request.content_type)
    
    tasks_triggered = []
    
    if request.url:
        task = process_single_tool_url.delay(str(request.url))
        tasks_triggered.append({"type": "single_url", "task_id": task.id})
    
    elif request.query:
        if request.content_type == "tool":
            task = process_single_tool_url.delay(request.query)
            tasks_triggered.append({"type": "tool_query", "task_id": task.id})
        elif request.content_type == "news":
            task = process_news_query.delay(request.query)
            tasks_triggered.append({"type": "news_query", "task_id": task.id})
    
    else:
        task = start_full_content_pipeline.delay()
        tasks_triggered.append({"type": "full_pipeline", "task_id": task.id})
    
    return {
        "status": "triggered",
        "tasks": tasks_triggered,
    }


@router.get("/pipeline/status/{task_id}", tags=["Admin"])
async def get_pipeline_status(task_id: str):
    """
    Get status of a pipeline task.
    """
    from app.core.celery_app import celery_app
    
    result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@router.get("/scraper/sources", tags=["Admin"])
async def list_scraper_sources():
    """
    List all configured scraper sources and their status.
    """
    from app.agents.scraper.sources import SCRAPER_SOURCES
    
    return {
        "sources": [
            {
                "name": s.name,
                "type": s.source_type,
                "url": s.base_url,
                "enabled": s.enabled,
            }
            for s in SCRAPER_SOURCES
        ]
    }


@router.get("/drafts", tags=["Admin"])
async def list_content_drafts(
    status: str = Query("draft", pattern="^(draft|approved|rejected)$"),
    content_type: str = Query(None, pattern="^(tool|news)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List content drafts awaiting review.
    """
    if not DatabaseService.is_configured():
        return {"drafts": [], "total": 0, "message": "Database not configured"}
    
    try:
        drafts = []
        
        if content_type is None or content_type == "tool":
            tools_repo = get_tools_repo()
            tool_drafts = await tools_repo.list_drafts(limit=limit)
            for tool in tool_drafts:
                drafts.append({
                    "id": tool["id"],
                    "type": "tool",
                    "title": tool.get("title", "Unknown"),
                    "url": tool.get("url"),
                    "status": tool.get("status", "draft"),
                    "trust_score": tool.get("trust_score"),
                    "created_at": tool.get("created_at"),
                })
        
        return {
            "drafts": drafts,
            "total": len(drafts),
            "status_filter": status,
        }
    except Exception as e:
        logger.error("Failed to list drafts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list drafts")


@router.post("/drafts/{draft_id}/action", tags=["Admin"])
async def action_content_draft(draft_id: str, request: ContentApprovalRequest):
    """
    Approve, reject, or regenerate a content draft.
    """
    logger.info("Draft action", draft_id=draft_id, action=request.action)
    
    if not DatabaseService.is_configured():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        tools_repo = get_tools_repo()
        
        if request.action == "approve":
            result = await tools_repo.approve(draft_id)
        elif request.action == "reject":
            result = await tools_repo.reject(draft_id)
        elif request.action == "regenerate":
            # Trigger regeneration task
            from app.tasks.pipeline_tasks import process_single_tool_url
            tool = await tools_repo.get_by_id(draft_id)
            if tool and tool.get("url"):
                process_single_tool_url.delay(tool["url"])
            result = {"id": draft_id, "status": "regenerating"}
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {
            "draft_id": draft_id,
            "action": request.action,
            "status": "processed",
            "result": result,
        }
    except Exception as e:
        logger.error("Failed to process draft action", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process action")


# =============================================
# Frontend Content API (Live Data)
# =============================================

@router.get("/content/tools", tags=["Content"])
async def get_content_tools(
    vertical: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get published tools for frontend consumption.
    Returns data in MDX-compatible format.
    """
    from app.services.publisher import MDXPublisher
    import os
    import yaml
    from pathlib import Path
    
    publisher = MDXPublisher()
    tools = []
    
    # Read from published MDX files
    tools_dir = publisher.tools_dir
    if tools_dir.exists():
        for mdx_file in tools_dir.glob("*.mdx"):
            try:
                content = mdx_file.read_text()
                # Parse frontmatter
                if content.startswith("---"):
                    _, frontmatter, body = content.split("---", 2)
                    data = yaml.safe_load(frontmatter)
                    data["content"] = body.strip()[:500]  # First 500 chars
                    
                    # Apply filters
                    if vertical and data.get("vertical") != vertical:
                        continue
                    if category and category not in data.get("categories", []):
                        continue
                    
                    tools.append(data)
            except Exception as e:
                logger.warning("Failed to parse tool MDX", file=mdx_file.name, error=str(e))
    
    # Sort by trust score descending
    tools.sort(key=lambda x: x.get("trustScore", 0), reverse=True)
    
    return {
        "count": len(tools[:limit]),
        "tools": tools[:limit],
        "lastUpdated": datetime.utcnow().isoformat(),
    }


@router.get("/content/news", tags=["Content"])
async def get_content_news(
    vertical: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get published news for frontend consumption.
    Returns data in MDX-compatible format.
    """
    from app.services.publisher import MDXPublisher
    import yaml
    
    publisher = MDXPublisher()
    news = []
    
    # Read from published MDX files
    news_dir = publisher.news_dir
    if news_dir.exists():
        for mdx_file in news_dir.glob("*.mdx"):
            try:
                content = mdx_file.read_text()
                # Parse frontmatter
                if content.startswith("---"):
                    _, frontmatter, body = content.split("---", 2)
                    data = yaml.safe_load(frontmatter)
                    data["content"] = body.strip()[:1000]  # First 1000 chars
                    
                    # Apply filters
                    if vertical and data.get("vertical") != vertical:
                        continue
                    
                    news.append(data)
            except Exception as e:
                logger.warning("Failed to parse news MDX", file=mdx_file.name, error=str(e))
    
    # Sort by publishedAt descending
    news.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    
    return {
        "count": len(news[:limit]),
        "news": news[:limit],
        "lastUpdated": datetime.utcnow().isoformat(),
    }


@router.get("/content/stats", tags=["Content"])
async def get_content_stats():
    """
    Get content statistics for dashboard.
    """
    from app.services.publisher import MDXPublisher
    
    publisher = MDXPublisher()
    
    return {
        "tools": len(publisher.list_published_tools()),
        "news": len(publisher.list_published_news()),
        "lastUpdated": datetime.utcnow().isoformat(),
    }


@router.post("/content/sync", tags=["Content", "Admin"])
async def sync_content():
    """
    Force sync content from database to MDX files.
    Admin endpoint for manual content refresh.
    """
    from app.services.publisher import MDXPublisher, ContentDraftStore
    from app.models import ToolData, NewsData, ContentStatus
    
    publisher = MDXPublisher()
    draft_store = ContentDraftStore()
    
    synced = {"tools": 0, "news": 0}
    
    # Get approved drafts
    drafts = draft_store.list_drafts(status=ContentStatus.APPROVED.value)
    
    for draft in drafts:
        try:
            if draft["type"] == "tool":
                tool_data = ToolData(**draft["data"])
                publisher.publish_tool(tool_data)
                synced["tools"] += 1
            elif draft["type"] == "news":
                news_data = NewsData(**draft["data"])
                publisher.publish_news(news_data)
                synced["news"] += 1
        except Exception as e:
            logger.warning("Failed to sync draft", draft_id=draft["id"], error=str(e))
    
    return {
        "status": "synced",
        "synced": synced,
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================
# Health & Stats
# =============================================

@router.get("/health", tags=["System"])
async def health_check():
    """
    API health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@router.get("/stats", tags=["System"])
async def get_platform_stats():
    """
    Get platform statistics.
    """
    stats = {
        "newsletter_subscribers": 0,
        "tools_indexed": 0,
        "tools_pending": 0,
        "news_articles": 0,
        "podcasts": 15,  # From curated list
        "sources_monitored": 20,
    }
    
    # Get stats from database if configured
    if DatabaseService.is_configured():
        try:
            tools_repo = get_tools_repo()
            subscribers_repo = get_subscribers_repo()
            
            tool_counts = await tools_repo.count_by_status()
            stats["tools_indexed"] = tool_counts.get("approved", 0)
            stats["tools_pending"] = tool_counts.get("draft", 0)
            stats["newsletter_subscribers"] = await subscribers_repo.count()
        except Exception as e:
            logger.warning("Failed to get DB stats", error=str(e))
    
    # Try Beehiiv for subscriber count as fallback
    if stats["newsletter_subscribers"] == 0:
        try:
            newsletter_service = NewsletterService()
            stats["newsletter_subscribers"] = await newsletter_service.get_subscriber_count()
        except:
            pass
    
    return stats
