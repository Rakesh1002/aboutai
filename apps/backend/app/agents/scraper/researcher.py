"""
Researcher Agent

Responsible for:
1. Searching the web via SearXNG
2. Scraping content from various sources
3. Extracting and organizing raw data for the pipeline
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import feedparser
from bs4 import BeautifulSoup
import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.agents.scraper.sources import (
    ScraperSource,
    SourceType,
    get_sources_by_type,
    get_enabled_sources,
)
from app.core.config import settings


class ResearcherAgent(BaseAgent):
    """
    Researcher/Scraper Agent
    
    Gathers raw content from multiple sources:
    - SearXNG metasearch
    - RSS feeds
    - Web scraping with Playwright
    - APIs (HackerNews, etc.)
    """
    
    name = "researcher"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.searxng_url = settings.SEARXNG_URL
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": settings.USER_AGENT},
        )
    
    async def process(self, context: AgentContext) -> AgentResult:
        """
        Main research process.
        
        Depending on content_type and source_url, either:
        - Scrape a specific URL
        - Search and aggregate from multiple sources
        """
        try:
            if context.source_url:
                # Scrape specific URL
                data = await self.scrape_url(context.source_url)
                context.raw_content = data.get("text", "")
                context.metadata["scraped_data"] = data
            else:
                # Aggregate from multiple sources
                data = await self.aggregate_sources(context.content_type)
                context.metadata["aggregated_data"] = data
            
            # Enrich with SearXNG search if we have a topic
            if context.metadata.get("search_query"):
                search_results = await self.search(context.metadata["search_query"])
                context.metadata["search_results"] = search_results
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output={
                    "source_url": context.source_url,
                    "raw_content_length": len(context.raw_content or ""),
                    "sources_scraped": len(context.metadata.get("aggregated_data", [])),
                },
            )
            
        except Exception as e:
            self.logger.error("Research failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    # ===========================================
    # SearXNG Search
    # ===========================================
    
    async def search(
        self,
        query: str,
        categories: List[str] = None,
        engines: List[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search using SearXNG metasearch engine.
        
        Args:
            query: Search query
            categories: List of categories ("general", "news", "science", "it")
            engines: Specific engines to use
            limit: Max results
            
        Returns:
            List of search results
        """
        params = {
            "q": query,
            "format": "json",
            "pageno": 1,
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
            
            self.logger.info(
                "SearXNG search completed",
                query=query,
                results_count=len(results),
            )
            
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("content", ""),
                    "source": r.get("engine", "unknown"),
                    "published_date": r.get("publishedDate"),
                }
                for r in results
            ]
            
        except Exception as e:
            self.logger.error("SearXNG search failed", query=query, error=str(e))
            return []
    
    async def search_ai_tools(self, query: str = "AI tools") -> List[Dict[str, Any]]:
        """Search specifically for AI tools"""
        return await self.search(
            query=f"{query} AI tool",
            categories=["it"],
            engines=["google", "bing", "duckduckgo"],
            limit=30,
        )
    
    async def search_ai_news(self, query: str = "artificial intelligence") -> List[Dict[str, Any]]:
        """Search specifically for AI news"""
        return await self.search(
            query=query,
            categories=["news"],
            engines=["google news", "bing news"],
            limit=30,
        )
    
    # ===========================================
    # URL Scraping
    # ===========================================
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a specific URL.
        Uses trafilatura for content extraction.
        """
        try:
            import trafilatura
            
            # Fetch the page
            response = await self.http_client.get(url)
            response.raise_for_status()
            html = response.text
            
            # Extract main content using trafilatura
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                include_links=True,
            )
            
            # Also parse with BeautifulSoup for metadata
            soup = BeautifulSoup(html, "lxml")
            
            # Extract metadata
            title = soup.title.string if soup.title else ""
            
            meta_desc = soup.find("meta", {"name": "description"})
            description = meta_desc["content"] if meta_desc else ""
            
            # Extract all links
            links = [
                {"href": a.get("href"), "text": a.get_text(strip=True)}
                for a in soup.find_all("a", href=True)
                if a.get("href", "").startswith("http")
            ]
            
            return {
                "url": url,
                "title": title,
                "description": description,
                "text": text or "",
                "links": links[:50],  # Limit links
                "html_length": len(html),
                "scraped_at": datetime.utcnow().isoformat(),
                "success": True,
            }
            
        except Exception as e:
            self.logger.error("URL scrape failed", url=url, error=str(e))
            return {
                "url": url,
                "success": False,
                "error": str(e),
            }
    
    async def scrape_with_browser(self, url: str) -> Dict[str, Any]:
        """Scrape URL using Playwright (for JS-heavy sites)"""
        from app.agents.scraper.browser import BrowserManager
        
        browser = BrowserManager()
        await browser.initialize()
        
        try:
            result = await browser.scrape_page(url)
            return result
        finally:
            await browser.close()
    
    # ===========================================
    # RSS Feed Scraping
    # ===========================================
    
    async def scrape_rss_feed(self, source: ScraperSource) -> List[Dict[str, Any]]:
        """Scrape an RSS feed"""
        if not source.rss_url:
            return []
        
        try:
            response = await self.http_client.get(source.rss_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            items = []
            for entry in feed.entries[:50]:  # Limit to 50 items
                item = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "description": entry.get("summary", ""),
                    "source": source.name,
                    "published_date": entry.get("published", ""),
                    "author": entry.get("author", ""),
                }
                
                # Apply content filters if defined
                if source.content_filters:
                    content = f"{item['title']} {item['description']}".lower()
                    if any(f.lower() in content for f in source.content_filters):
                        items.append(item)
                else:
                    items.append(item)
            
            self.logger.info(
                "RSS feed scraped",
                source=source.name,
                items_count=len(items),
            )
            
            return items
            
        except Exception as e:
            self.logger.error(
                "RSS scrape failed",
                source=source.name,
                error=str(e),
            )
            return []
    
    # ===========================================
    # API Scraping
    # ===========================================
    
    async def scrape_hacker_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Scrape top AI-related stories from Hacker News"""
        try:
            # Get top story IDs
            response = await self.http_client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            story_ids = response.json()[:100]  # Check top 100
            
            ai_keywords = [
                "ai", "gpt", "llm", "claude", "openai", "anthropic",
                "machine learning", "neural", "chatbot", "artificial intelligence",
            ]
            
            items = []
            for story_id in story_ids:
                if len(items) >= limit:
                    break
                
                story_response = await self.http_client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                )
                story = story_response.json()
                
                if not story or story.get("type") != "story":
                    continue
                
                title = story.get("title", "").lower()
                if any(kw in title for kw in ai_keywords):
                    items.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "Hacker News",
                        "score": story.get("score", 0),
                        "comments": story.get("descendants", 0),
                        "author": story.get("by", ""),
                    })
            
            return items
            
        except Exception as e:
            self.logger.error("HN scrape failed", error=str(e))
            return []
    
    # ===========================================
    # Aggregation
    # ===========================================
    
    async def aggregate_sources(
        self,
        content_type: str,
        sources: List[ScraperSource] = None,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate content from multiple sources.
        
        Args:
            content_type: "tool" or "news"
            sources: Specific sources to use (or all enabled sources)
            
        Returns:
            List of aggregated content items
        """
        if sources is None:
            if content_type == "news":
                sources = get_sources_by_type(SourceType.RSS) + get_sources_by_type(SourceType.NEWS)
            else:
                sources = get_sources_by_type(SourceType.DIRECTORY)
        
        all_items = []
        
        # Scrape RSS feeds in parallel
        rss_sources = [s for s in sources if s.source_type == SourceType.RSS]
        if rss_sources:
            tasks = [self.scrape_rss_feed(s) for s in rss_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_items.extend(result)
        
        # Scrape HackerNews if enabled
        hn_source = next((s for s in sources if s.name == "Hacker News"), None)
        if hn_source and hn_source.enabled:
            hn_items = await self.scrape_hacker_news()
            all_items.extend(hn_items)
        
        # Add SearXNG search results
        if content_type == "news":
            search_results = await self.search_ai_news()
            all_items.extend(search_results)
        else:
            search_results = await self.search_ai_tools()
            all_items.extend(search_results)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
        
        self.logger.info(
            "Aggregation completed",
            content_type=content_type,
            total_items=len(unique_items),
        )
        
        return unique_items
    
    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()

