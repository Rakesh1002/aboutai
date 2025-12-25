"""
Content Celery Tasks

Background tasks for content publishing and management.
"""
from celery import shared_task
import structlog

from app.core.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(bind=True, name="app.tasks.content_tasks.publish_approved_content")
def publish_approved_content(self):
    """
    Publish all approved content drafts to the frontend.
    Runs hourly.
    """
    import asyncio
    from app.services.content import ContentService
    from app.services.publisher import PublisherService
    
    logger.info("Publishing approved content")
    
    async def run_publish():
        content_service = ContentService()
        publisher = PublisherService()
        
        # Get approved drafts
        approved_drafts = await content_service.get_approved_drafts()
        
        published = []
        for draft in approved_drafts:
            try:
                # Publish to MDX file
                result = await publisher.publish_draft(draft)
                
                # Mark as published
                await content_service.mark_as_published(draft["id"])
                
                published.append({
                    "draft_id": draft["id"],
                    "file_path": result.get("file_path"),
                    "status": "published",
                })
                
            except Exception as e:
                logger.error("Failed to publish draft", draft_id=draft["id"], error=str(e))
        
        return {
            "total_approved": len(approved_drafts),
            "published": len(published),
            "results": published,
        }
    
    return asyncio.run(run_publish())


@celery_app.task(bind=True, name="app.tasks.content_tasks.generate_newsletter_draft")
def generate_newsletter_draft(self):
    """
    Generate a newsletter draft from recent content.
    """
    import asyncio
    from app.services.content import ContentService
    from app.services.newsletter import NewsletterService
    
    logger.info("Generating newsletter draft")
    
    async def run_generate():
        content_service = ContentService()
        newsletter_service = NewsletterService()
        
        # Get recent published content
        recent_tools = await content_service.get_recent_published(content_type="tool", limit=5)
        recent_news = await content_service.get_recent_published(content_type="news", limit=10)
        
        # Generate newsletter
        draft = await newsletter_service.generate_draft(
            tools=recent_tools,
            news=recent_news,
        )
        
        return {
            "draft_id": draft.get("id"),
            "tools_included": len(recent_tools),
            "news_included": len(recent_news),
        }
    
    return asyncio.run(run_generate())


@celery_app.task(bind=True, name="app.tasks.content_tasks.sync_to_frontend")
def sync_to_frontend(self):
    """
    Sync all published content to the frontend MDX directory.
    """
    import asyncio
    from app.services.publisher import PublisherService
    
    logger.info("Syncing content to frontend")
    
    async def run_sync():
        publisher = PublisherService()
        result = await publisher.full_sync()
        return result
    
    return asyncio.run(run_sync())


@celery_app.task(bind=True, name="app.tasks.content_tasks.cleanup_old_drafts")
def cleanup_old_drafts(self):
    """
    Clean up old rejected/expired drafts.
    """
    import asyncio
    from app.services.content import ContentService
    
    logger.info("Cleaning up old drafts")
    
    async def run_cleanup():
        content_service = ContentService()
        
        # Delete drafts older than 30 days that are rejected/archived
        deleted = await content_service.cleanup_old_drafts(days=30)
        
        return {
            "deleted_count": deleted,
        }
    
    return asyncio.run(run_cleanup())

