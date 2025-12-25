"""
Content Service

Manages content storage, retrieval, and lifecycle.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import structlog

from app.core.redis import redis_client
from app.core.config import settings
from app.models.content import ContentStatus


class ContentService:
    """
    Content service for managing tools and news content.
    """
    
    def __init__(self):
        self.logger = structlog.get_logger().bind(service="content")
    
    # ===========================================
    # Draft Management
    # ===========================================
    
    async def save_draft(self, context) -> str:
        """Save a content draft from pipeline context"""
        draft_id = str(uuid.uuid4())
        
        draft_data = {
            "id": draft_id,
            "content_type": context.content_type,
            "source_url": context.source_url or "",
            "status": ContentStatus.PENDING_REVIEW.value,
            "pipeline_id": context.pipeline_id,
            "created_at": datetime.utcnow().isoformat(),
            "processed_content": str(context.processed_content),
            "mdx_content": context.metadata.get("final_mdx", context.metadata.get("mdx_content", "")),
            "quality_score": str(context.processed_content.get("quality_score", 0)),
        }
        
        # Store in Redis
        await redis_client.hset(f"draft:{draft_id}", mapping=draft_data)
        
        # Add to pending queue
        await redis_client.lpush("drafts:pending", draft_id)
        
        self.logger.info("Draft saved", draft_id=draft_id, content_type=context.content_type)
        
        return draft_id
    
    async def list_drafts(
        self,
        content_type: str = None,
        status: str = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List content drafts"""
        # Get all draft IDs
        draft_ids = await redis_client.lrange("drafts:pending", 0, limit - 1)
        
        drafts = []
        for draft_id in draft_ids:
            draft_data = await redis_client.hgetall(f"draft:{draft_id}")
            if draft_data:
                # Filter by content_type if specified
                if content_type and draft_data.get("content_type") != content_type:
                    continue
                # Filter by status if specified
                if status and draft_data.get("status") != status:
                    continue
                
                drafts.append({
                    "id": draft_id,
                    "type": draft_data.get("content_type"),
                    "title": draft_data.get("title", "Untitled"),
                    "slug": draft_data.get("slug", ""),
                    "status": draft_data.get("status"),
                    "quality_score": draft_data.get("quality_score"),
                    "created_at": draft_data.get("created_at"),
                })
        
        return drafts
    
    async def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific draft"""
        draft_data = await redis_client.hgetall(f"draft:{draft_id}")
        return draft_data if draft_data else None
    
    async def approve_draft(self, draft_id: str) -> Dict[str, Any]:
        """Approve a draft for publication"""
        await redis_client.hset(f"draft:{draft_id}", "status", ContentStatus.APPROVED.value)
        
        # Move to approved queue
        await redis_client.lrem("drafts:pending", 0, draft_id)
        await redis_client.lpush("drafts:approved", draft_id)
        
        self.logger.info("Draft approved", draft_id=draft_id)
        
        return {"status": "approved", "draft_id": draft_id}
    
    async def reject_draft(self, draft_id: str, reason: str = None) -> Dict[str, Any]:
        """Reject a draft"""
        update_data = {"status": ContentStatus.REJECTED.value}
        if reason:
            update_data["rejection_reason"] = reason
        
        await redis_client.hset(f"draft:{draft_id}", mapping=update_data)
        
        # Remove from pending queue
        await redis_client.lrem("drafts:pending", 0, draft_id)
        
        self.logger.info("Draft rejected", draft_id=draft_id, reason=reason)
        
        return {"status": "rejected", "draft_id": draft_id}
    
    async def regenerate_draft(self, draft_id: str) -> str:
        """Regenerate a draft through the pipeline"""
        draft_data = await redis_client.hgetall(f"draft:{draft_id}")
        
        if not draft_data:
            raise ValueError(f"Draft not found: {draft_id}")
        
        # Queue for re-processing
        from app.tasks.pipeline_tasks import run_content_pipeline
        task = run_content_pipeline.delay()
        
        return task.id
    
    async def get_approved_drafts(self) -> List[Dict[str, Any]]:
        """Get all approved drafts ready for publishing"""
        draft_ids = await redis_client.lrange("drafts:approved", 0, -1)
        
        drafts = []
        for draft_id in draft_ids:
            draft_data = await redis_client.hgetall(f"draft:{draft_id}")
            if draft_data:
                drafts.append(draft_data)
        
        return drafts
    
    async def mark_as_published(self, draft_id: str):
        """Mark a draft as published"""
        await redis_client.hset(f"draft:{draft_id}", "status", ContentStatus.PUBLISHED.value)
        await redis_client.hset(f"draft:{draft_id}", "published_at", datetime.utcnow().isoformat())
        
        # Remove from approved queue
        await redis_client.lrem("drafts:approved", 0, draft_id)
        
        self.logger.info("Draft published", draft_id=draft_id)
    
    # ===========================================
    # Queue Management
    # ===========================================
    
    async def queue_for_processing(self, item: Dict[str, Any], content_type: str):
        """Queue an item for pipeline processing"""
        item_id = str(uuid.uuid4())
        item["id"] = item_id
        item["content_type"] = content_type
        item["queued_at"] = datetime.utcnow().isoformat()
        
        # Store item data
        await redis_client.hset(f"queue:item:{item_id}", mapping={
            k: str(v) if not isinstance(v, str) else v
            for k, v in item.items()
        })
        
        # Add to processing queue
        await redis_client.lpush("queue:processing", item_id)
        
        return item_id
    
    async def get_queued_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get items queued for processing"""
        item_ids = await redis_client.lrange("queue:processing", 0, limit - 1)
        
        items = []
        for item_id in item_ids:
            item_data = await redis_client.hgetall(f"queue:item:{item_id}")
            if item_data:
                items.append(item_data)
        
        return items
    
    # ===========================================
    # Published Content Management
    # ===========================================
    
    async def get_all_published_tools(self) -> List[Dict[str, Any]]:
        """Get all published tools (placeholder - would use database)"""
        # In production, this would query Supabase
        return []
    
    async def get_tools_needing_score_update(self) -> List[Dict[str, Any]]:
        """Get tools that need trust score updates"""
        # Tools not updated in the last 7 days
        return []
    
    async def update_tool_score(self, tool_id: str, score_data: Dict[str, Any]):
        """Update a tool's trust score"""
        self.logger.info("Updating tool score", tool_id=tool_id, score=score_data.get("total"))
    
    async def get_recent_published(
        self,
        content_type: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get recently published content"""
        # Placeholder - would query database
        return []
    
    async def cleanup_old_drafts(self, days: int = 30) -> int:
        """Clean up old drafts"""
        # Placeholder - would delete old rejected drafts
        return 0

