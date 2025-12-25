"""
Search Service

Provides search functionality using SearXNG.
Replaces Algolia with self-hosted search.
"""
from typing import List, Dict, Any, Optional
import httpx
import structlog

from app.core.config import settings


class SearchService:
    """
    Search service using SearXNG metasearch engine.
    
    SearXNG provides:
    - Privacy-respecting search
    - Multiple search engine aggregation
    - No external dependencies (self-hosted)
    - JSON API for programmatic access
    """
    
    def __init__(self):
        self.logger = structlog.get_logger().bind(service="search")
        self.searxng_url = settings.SEARXNG_URL
        self.http_client = httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": settings.USER_AGENT},
        )
    
    async def search(
        self,
        query: str,
        categories: List[str] = None,
        engines: List[str] = None,
        limit: int = 20,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Perform a search query.
        
        Args:
            query: Search query string
            categories: List of categories to search (general, news, science, it)
            engines: Specific engines to use
            limit: Maximum results to return
            page: Page number for pagination
            
        Returns:
            List of search results
        """
        params = {
            "q": query,
            "format": "json",
            "pageno": page,
        }
        
        if categories:
            params["categories"] = ",".join(categories)
        if engines:
            params["engines"] = ",".join(engines)
        
        try:
            response = await self.http_client.get(
                f"{self.searxng_url}/search",
                params=params,
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])[:limit]
            
            # Transform to consistent format
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("content", ""),
                    "source": r.get("engine", "unknown"),
                    "score": r.get("score"),
                    "published_date": r.get("publishedDate"),
                    "thumbnail": r.get("thumbnail"),
                }
                for r in results
            ]
            
        except Exception as e:
            self.logger.error("Search failed", query=query, error=str(e))
            return []
    
    async def search_tools(
        self,
        query: str,
        vertical: str = None,
        category: str = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search for AI tools.
        """
        # Enhance query with AI tool context
        enhanced_query = f"{query} AI tool"
        if vertical:
            enhanced_query += f" {vertical}"
        if category:
            enhanced_query += f" {category}"
        
        return await self.search(
            query=enhanced_query,
            categories=["it"],
            engines=["google", "bing", "duckduckgo"],
            limit=limit,
        )
    
    async def search_news(
        self,
        query: str = "artificial intelligence",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search for AI news.
        """
        return await self.search(
            query=query,
            categories=["news"],
            engines=["google news", "bing news"],
            limit=limit,
        )
    
    async def get_suggestions(
        self,
        query: str,
        limit: int = 10,
    ) -> List[str]:
        """
        Get search suggestions/autocomplete.
        """
        try:
            response = await self.http_client.get(
                f"{self.searxng_url}/autocompleter",
                params={"q": query},
            )
            response.raise_for_status()
            
            suggestions = response.json()
            return suggestions[:limit] if isinstance(suggestions, list) else []
            
        except Exception as e:
            self.logger.error("Suggestions failed", query=query, error=str(e))
            return []
    
    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()

