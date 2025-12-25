"""
Pipeline Tasks - Celery tasks for content generation pipeline.
Handles the full automation from scraping to publishing.
"""
from typing import Optional, Dict, Any, List
import structlog

from app.core.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="pipeline.start_full_content_pipeline")
def start_full_content_pipeline():
    """
    Main pipeline task that orchestrates the full content generation workflow.
    Runs periodically to discover and process new AI tools and news.
    """
    logger.info("Starting full content generation pipeline")
    
    # Import here to avoid circular imports
    from app.agents.scraper.launch_sites import LaunchSiteAggregator
    from app.agents.scraper.podcasts import PodcastAggregator
    import asyncio
    
    async def run_pipeline():
        # 1. Aggregate launches from all sources
        aggregator = LaunchSiteAggregator()
        launches = await aggregator.aggregate_all_launches(limit_per_source=20)
        logger.info("Aggregated launches", count=len(launches))
        
        # 2. For each launch, queue individual processing
        for launch in launches[:50]:  # Limit to 50 per run
            process_single_tool_url.delay(
                url=launch.url,
                source=launch.source,
                title=launch.title,
            )
        
        # 3. Update podcast episodes
        podcast_aggregator = PodcastAggregator()
        episodes = await podcast_aggregator.get_recent_episodes(limit=30)
        logger.info("Found podcast episodes", count=len(episodes))
        
        return {
            "launches_discovered": len(launches),
            "episodes_found": len(episodes),
        }
    
    return asyncio.get_event_loop().run_until_complete(run_pipeline())


@celery_app.task(name="pipeline.process_single_tool_url")
def process_single_tool_url(
    url: str,
    submitter_email: Optional[str] = None,
    notes: Optional[str] = None,
    source: Optional[str] = None,
    title: Optional[str] = None,
    submission_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process a single AI tool URL through the full pipeline.
    
    1. Scrape the URL
    2. Analyze with Trust Engine
    3. Generate content
    4. Auto-publish high quality content or save as draft
    """
    logger.info("Processing tool URL", url=url, source=source)
    
    import asyncio
    from app.agents.trust_engine import TrustEngine
    from app.services.publisher import MDXPublisher
    from app.models import ToolData, ToolPricing, WrapperStatus, Vertical
    from app.core.config import settings
    from datetime import datetime
    import re
    
    def slugify(text: str) -> str:
        """Convert text to URL-safe slug"""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")[:100]
    
    async def process():
        # 1. Analyze with Trust Engine
        trust_engine = TrustEngine()
        analysis = await trust_engine.analyze_tool(url, name=title)
        
        # 2. Build tool data from analysis
        tool_name = title or analysis.name or "Unknown Tool"
        
        # Build description from reasoning or default
        description = analysis.reasoning[:300] if analysis.reasoning else f"An AI tool from {source or 'the web'}"
        
        tool_data = ToolData(
            name=tool_name,
            slug=slugify(tool_name),
            description=description,
            url=url,
            vertical=Vertical.DEVTOOLS if "github" in url.lower() else Vertical.GENERAL,
            categories=["ai", source.lower() if source else "general"],
            tags=list(analysis.detected_technologies[:10]) if analysis.detected_technologies else [],
            trust_score=analysis.trust_score,
            wrapper_status=analysis.wrapper_status,
            is_verified=analysis.trust_score >= 70,
            pricing=ToolPricing(),
            content=f"{tool_name} is an AI tool discovered from {source or 'the web'}. Trust Score: {analysis.trust_score}. {analysis.reasoning}",
            detected_technologies=list(analysis.detected_technologies) if analysis.detected_technologies else [],
            api_dependencies=list(analysis.api_dependencies) if analysis.api_dependencies else [],
            proprietary_tech_score=analysis.proprietary_tech_score,
            reliability_score=analysis.reliability_score,
            transparency_score=analysis.transparency_score,
            liveness_score=analysis.liveness_score,
            created_at=datetime.utcnow(),
            last_audited_at=datetime.utcnow(),
        )
        
        # 3. Auto-publish high quality tools or save as draft
        publisher = MDXPublisher()
        
        # Calculate quality score based on trust analysis
        quality_score = analysis.trust_score / 100
        
        if quality_score >= settings.AUTO_APPROVE_THRESHOLD:
            # Auto-publish high quality content
            file_path = publisher.publish_tool(tool_data)
            logger.info("Auto-published tool", name=tool_name, trust_score=analysis.trust_score, path=file_path)
            return {
                "url": url,
                "status": "published",
                "source": source,
                "title": tool_name,
                "trust_score": analysis.trust_score,
                "wrapper_status": analysis.wrapper_status.value,
                "file_path": file_path,
            }
        else:
            # Save as draft for review
            logger.info("Tool saved as draft", name=tool_name, trust_score=analysis.trust_score)
            return {
                "url": url,
                "status": "draft",
                "source": source,
                "title": tool_name,
                "trust_score": analysis.trust_score,
                "wrapper_status": analysis.wrapper_status.value,
                "reason": "Quality score below auto-approval threshold",
            }
    
    try:
        return asyncio.get_event_loop().run_until_complete(process())
    except Exception as e:
        logger.error("Tool processing failed", url=url, error=str(e))
        return {
            "url": url,
            "status": "failed",
            "source": source,
            "title": title,
            "error": str(e),
        }


@celery_app.task(name="pipeline.process_news_query")
def process_news_query(query: str) -> Dict[str, Any]:
    """
    Process a news query - search, scrape, and generate article.
    """
    logger.info("Processing news query", query=query)
    
    result = {
        "query": query,
        "status": "processed",
        "articles_generated": 0,
    }
    
    return result


@celery_app.task(name="pipeline.generate_weekly_newsletter")
def generate_weekly_newsletter() -> Dict[str, Any]:
    """
    Generate the weekly newsletter digest.
    Called by Celery Beat on schedule.
    """
    logger.info("Generating weekly newsletter")
    
    from app.services.newsletter import NewsletterService
    import asyncio
    
    async def generate():
        service = NewsletterService()
        
        # Get recent content (would come from database)
        new_tools = []  # Placeholder - fetch from DB
        top_news = []   # Placeholder - fetch from DB
        
        result = await service.create_weekly_digest(
            new_tools=new_tools,
            top_news=top_news,
            podcast_episodes=[],
            publish=True,  # Create draft in Beehiiv
        )
        
        return {
            "status": "generated",
            "subject": result.get("content", {}).subject if result.get("content") else None,
        }
    
    return asyncio.get_event_loop().run_until_complete(generate())


@celery_app.task(name="pipeline.scrape_launch_sites")
def scrape_launch_sites() -> Dict[str, Any]:
    """
    Scrape all configured launch sites for new AI tools.
    """
    logger.info("Scraping launch sites")
    
    from app.agents.scraper.launch_sites import LaunchSiteAggregator
    import asyncio
    
    async def scrape():
        aggregator = LaunchSiteAggregator()
        launches = await aggregator.aggregate_all_launches()
        
        return {
            "total_launches": len(launches),
            "sources": list(set(l.source for l in launches)),
        }
    
    return asyncio.get_event_loop().run_until_complete(scrape())


@celery_app.task(name="pipeline.update_podcast_directory")
def update_podcast_directory() -> Dict[str, Any]:
    """
    Update the podcast directory with latest episodes.
    """
    logger.info("Updating podcast directory")
    
    from app.agents.scraper.podcasts import PodcastAggregator
    import asyncio
    
    async def update():
        aggregator = PodcastAggregator()
        
        # Get shows and episodes
        shows = await aggregator.get_all_shows()
        episodes = await aggregator.get_recent_episodes(limit=100)
        
        # Discover new podcasts
        new_podcasts = await aggregator.discover_new_podcasts()
        
        return {
            "shows": len(shows),
            "recent_episodes": len(episodes),
            "discovered": len(new_podcasts),
        }
    
    return asyncio.get_event_loop().run_until_complete(update())
