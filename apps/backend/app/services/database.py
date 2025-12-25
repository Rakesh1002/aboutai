"""
Supabase Database Service
Handles all database operations for tools, news, and submissions.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import structlog
from supabase import create_client, Client

from app.core.config import settings

logger = structlog.get_logger()


class DatabaseService:
    """Service for interacting with Supabase database."""
    
    _client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client."""
        if cls._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
                raise ValueError("Supabase credentials not configured")
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        return cls._client
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Supabase is configured."""
        return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


class ToolsRepository:
    """Repository for tool operations."""
    
    def __init__(self):
        self.db = DatabaseService.get_client()
        self.table = "tools"
    
    async def create(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool."""
        logger.info("Creating tool", title=tool_data.get("title"))
        
        result = self.db.table(self.table).insert(tool_data).execute()
        return result.data[0] if result.data else None
    
    async def get_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool by ID."""
        result = self.db.table(self.table).select("*").eq("id", tool_id).single().execute()
        return result.data
    
    async def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get tool by slug."""
        result = self.db.table(self.table).select("*").eq("slug", slug).single().execute()
        return result.data
    
    async def get_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get tool by URL (for deduplication)."""
        result = self.db.table(self.table).select("*").eq("url", url).single().execute()
        return result.data
    
    async def list_tools(
        self,
        status: str = "approved",
        category: Optional[str] = None,
        vertical: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List tools with optional filtering."""
        query = self.db.table(self.table).select("*").eq("status", status)
        
        if category:
            query = query.eq("category", category)
        if vertical:
            query = query.eq("vertical", vertical)
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []
    
    async def list_drafts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List tools pending review."""
        result = (
            self.db.table(self.table)
            .select("*")
            .eq("status", "draft")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    async def update(self, tool_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tool."""
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = self.db.table(self.table).update(updates).eq("id", tool_id).execute()
        return result.data[0] if result.data else None
    
    async def approve(self, tool_id: str) -> Dict[str, Any]:
        """Approve a tool for publishing."""
        return await self.update(tool_id, {"status": "approved"})
    
    async def reject(self, tool_id: str) -> Dict[str, Any]:
        """Reject a tool."""
        return await self.update(tool_id, {"status": "rejected"})
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Full-text search for tools."""
        # Use Supabase full-text search
        result = (
            self.db.table(self.table)
            .select("*")
            .eq("status", "approved")
            .text_search("title", query, config="english")
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    async def count_by_status(self) -> Dict[str, int]:
        """Get tool counts by status."""
        result = self.db.table(self.table).select("status", count="exact").execute()
        counts = {"draft": 0, "approved": 0, "rejected": 0}
        for row in result.data or []:
            if row.get("status") in counts:
                counts[row["status"]] = row.get("count", 0)
        return counts


class NewsRepository:
    """Repository for news article operations."""
    
    def __init__(self):
        self.db = DatabaseService.get_client()
        self.table = "news"
    
    async def create(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new news article."""
        logger.info("Creating news article", title=news_data.get("title"))
        result = self.db.table(self.table).insert(news_data).execute()
        return result.data[0] if result.data else None
    
    async def get_by_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Get news article by ID."""
        result = self.db.table(self.table).select("*").eq("id", news_id).single().execute()
        return result.data
    
    async def get_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get news by source URL (for deduplication)."""
        result = self.db.table(self.table).select("*").eq("source_url", url).single().execute()
        return result.data
    
    async def list_news(
        self,
        vertical: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List news articles."""
        query = self.db.table(self.table).select("*")
        
        if vertical:
            query = query.eq("vertical", vertical)
        
        query = query.order("published_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Full-text search for news."""
        result = (
            self.db.table(self.table)
            .select("*")
            .text_search("title", query, config="english")
            .limit(limit)
            .execute()
        )
        return result.data or []


class SubmissionsRepository:
    """Repository for tool submission operations."""
    
    def __init__(self):
        self.db = DatabaseService.get_client()
        self.table = "submissions"
    
    async def create(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new submission."""
        logger.info("Creating submission", url=submission_data.get("url"))
        result = self.db.table(self.table).insert(submission_data).execute()
        return result.data[0] if result.data else None
    
    async def get_by_id(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get submission by ID."""
        result = self.db.table(self.table).select("*").eq("id", submission_id).single().execute()
        return result.data
    
    async def list_pending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List pending submissions."""
        result = (
            self.db.table(self.table)
            .select("*")
            .eq("status", "pending")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    async def update_status(
        self,
        submission_id: str,
        status: str,
        tool_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update submission status."""
        updates = {"status": status, "processed_at": datetime.utcnow().isoformat()}
        if tool_id:
            updates["tool_id"] = tool_id
        result = self.db.table(self.table).update(updates).eq("id", submission_id).execute()
        return result.data[0] if result.data else None


class SubscribersRepository:
    """Repository for newsletter subscriber operations."""
    
    def __init__(self):
        self.db = DatabaseService.get_client()
        self.table = "subscribers"
    
    async def create(self, email: str, source: str = "website") -> Dict[str, Any]:
        """Add a new subscriber."""
        logger.info("Adding subscriber", email=email)
        result = self.db.table(self.table).upsert({
            "email": email,
            "source": source,
            "subscribed_at": datetime.utcnow().isoformat(),
        }).execute()
        return result.data[0] if result.data else None
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get subscriber by email."""
        result = self.db.table(self.table).select("*").eq("email", email).single().execute()
        return result.data
    
    async def count(self) -> int:
        """Get total subscriber count."""
        result = self.db.table(self.table).select("*", count="exact").execute()
        return result.count or 0
    
    async def list_all(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """List all subscribers."""
        result = (
            self.db.table(self.table)
            .select("*")
            .order("subscribed_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []


class PodcastsRepository:
    """Repository for podcast operations."""
    
    def __init__(self):
        self.db = DatabaseService.get_client()
        self.shows_table = "podcast_shows"
        self.episodes_table = "podcast_episodes"
    
    async def upsert_show(self, show_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a podcast show."""
        result = self.db.table(self.shows_table).upsert(show_data).execute()
        return result.data[0] if result.data else None
    
    async def upsert_episode(self, episode_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a podcast episode."""
        result = self.db.table(self.episodes_table).upsert(episode_data).execute()
        return result.data[0] if result.data else None
    
    async def list_shows(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all podcast shows."""
        result = (
            self.db.table(self.shows_table)
            .select("*")
            .order("title")
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    async def list_recent_episodes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent podcast episodes."""
        result = (
            self.db.table(self.episodes_table)
            .select("*, podcast_shows(title, image_url)")
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []


# Singleton instances
_tools_repo: Optional[ToolsRepository] = None
_news_repo: Optional[NewsRepository] = None
_submissions_repo: Optional[SubmissionsRepository] = None
_subscribers_repo: Optional[SubscribersRepository] = None
_podcasts_repo: Optional[PodcastsRepository] = None


def get_tools_repo() -> ToolsRepository:
    global _tools_repo
    if _tools_repo is None:
        _tools_repo = ToolsRepository()
    return _tools_repo


def get_news_repo() -> NewsRepository:
    global _news_repo
    if _news_repo is None:
        _news_repo = NewsRepository()
    return _news_repo


def get_submissions_repo() -> SubmissionsRepository:
    global _submissions_repo
    if _submissions_repo is None:
        _submissions_repo = SubmissionsRepository()
    return _submissions_repo


def get_subscribers_repo() -> SubscribersRepository:
    global _subscribers_repo
    if _subscribers_repo is None:
        _subscribers_repo = SubscribersRepository()
    return _subscribers_repo


def get_podcasts_repo() -> PodcastsRepository:
    global _podcasts_repo
    if _podcasts_repo is None:
        _podcasts_repo = PodcastsRepository()
    return _podcasts_repo

