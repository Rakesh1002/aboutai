"""
Data source definitions and scrapers for automated content ingestion.
Uses self-hostable open source tools: SearXNG, Playwright, feedparser, etc.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import feedparser
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import structlog
import asyncio
import json
import re

from app.core.config import settings

logger = structlog.get_logger()


class SourceType(Enum):
    RSS = "rss"
    API = "api"
    SCRAPE = "scrape"
    SEARCH = "search"
    SOCIAL = "social"


@dataclass
class SourceConfig:
    """Configuration for a content source"""
    name: str
    source_type: SourceType
    base_url: str
    enabled: bool = True
    rate_limit: int = 10  # requests per minute
    category: str = "general"  # news, tools, research
    vertical: str = "general"  # agtech, legal, devtools, marketing, general
    priority: int = 1  # 1 = highest
    selectors: Dict[str, str] = field(default_factory=dict)
    auth: Optional[Dict[str, str]] = None


# ===========================================
# RSS Feed Sources
# ===========================================

RSS_SOURCES: List[SourceConfig] = [
    # Tech News
    SourceConfig(
        name="TechCrunch AI",
        source_type=SourceType.RSS,
        base_url="https://techcrunch.com/category/artificial-intelligence/feed/",
        category="news",
        vertical="general",
        priority=1,
    ),
    SourceConfig(
        name="VentureBeat AI",
        source_type=SourceType.RSS,
        base_url="https://venturebeat.com/category/ai/feed/",
        category="news",
        vertical="general",
        priority=1,
    ),
    SourceConfig(
        name="MIT Tech Review AI",
        source_type=SourceType.RSS,
        base_url="https://www.technologyreview.com/topic/artificial-intelligence/feed",
        category="news",
        vertical="general",
        priority=1,
    ),
    SourceConfig(
        name="The Verge AI",
        source_type=SourceType.RSS,
        base_url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        category="news",
        vertical="general",
        priority=2,
    ),
    SourceConfig(
        name="Ars Technica AI",
        source_type=SourceType.RSS,
        base_url="https://feeds.arstechnica.com/arstechnica/technology-lab",
        category="news",
        vertical="general",
        priority=2,
    ),
    # Research
    SourceConfig(
        name="arXiv AI",
        source_type=SourceType.RSS,
        base_url="http://export.arxiv.org/rss/cs.AI",
        category="research",
        vertical="general",
        priority=1,
    ),
    SourceConfig(
        name="arXiv ML",
        source_type=SourceType.RSS,
        base_url="http://export.arxiv.org/rss/cs.LG",
        category="research",
        vertical="general",
        priority=1,
    ),
    # Developer Tools
    SourceConfig(
        name="GitHub Blog",
        source_type=SourceType.RSS,
        base_url="https://github.blog/feed/",
        category="news",
        vertical="devtools",
        priority=2,
    ),
    SourceConfig(
        name="Hacker News AI",
        source_type=SourceType.RSS,
        base_url="https://hnrss.org/newest?q=AI+OR+LLM+OR+machine+learning",
        category="news",
        vertical="devtools",
        priority=2,
    ),
]


# ===========================================
# Tool Directory Sources
# ===========================================

DIRECTORY_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Product Hunt AI",
        source_type=SourceType.SCRAPE,
        base_url="https://www.producthunt.com/topics/artificial-intelligence",
        category="tools",
        vertical="general",
        priority=1,
        selectors={
            "items": "[data-test='post-item']",
            "title": "h3",
            "description": "[data-test='tagline']",
            "url": "a[href^='/posts/']",
            "votes": "[data-test='vote-button'] span",
        },
    ),
    SourceConfig(
        name="GitHub Trending AI",
        source_type=SourceType.SCRAPE,
        base_url="https://github.com/trending?since=weekly&spoken_language_code=en",
        category="tools",
        vertical="devtools",
        priority=1,
        selectors={
            "items": "article.Box-row",
            "title": "h2 a",
            "description": "p",
            "url": "h2 a",
            "stars": "span.d-inline-block.float-sm-right",
        },
    ),
]


# ===========================================
# All Sources Combined
# ===========================================

SCRAPER_SOURCES = RSS_SOURCES + DIRECTORY_SOURCES


# ===========================================
# RSS Feed Parser
# ===========================================

class RSSFeedParser:
    """
    Self-hosted RSS feed parser using feedparser (open source).
    No external API dependencies.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def parse_feed(self, source: SourceConfig) -> List[Dict[str, Any]]:
        """Parse an RSS feed and return structured items"""
        logger.info("Parsing RSS feed", source=source.name, url=source.base_url)
        
        try:
            response = await self.client.get(source.base_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            items = []
            
            for entry in feed.entries[:50]:  # Limit to 50 items
                item = {
                    "source": source.name,
                    "source_type": source.source_type.value,
                    "category": source.category,
                    "vertical": source.vertical,
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "description": self._clean_html(entry.get("summary", "")),
                    "published_at": self._parse_date(entry.get("published", "")),
                    "author": entry.get("author", source.name),
                    "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
                    "raw_content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "",
                }
                items.append(item)
            
            logger.info("Parsed RSS feed", source=source.name, items=len(items))
            return items
            
        except Exception as e:
            logger.error("Failed to parse RSS feed", source=source.name, error=str(e))
            return []
    
    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from string"""
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)[:500]
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            from dateutil.parser import parse
            return parse(date_str).isoformat()
        except:
            return datetime.utcnow().isoformat()
    
    async def parse_all_feeds(self) -> List[Dict[str, Any]]:
        """Parse all configured RSS feeds"""
        all_items = []
        tasks = []
        
        for source in RSS_SOURCES:
            if source.enabled:
                tasks.append(self.parse_feed(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        return all_items


# ===========================================
# GitHub Scraper
# ===========================================

class GitHubScraper:
    """
    GitHub API scraper for trending repositories and AI tools.
    Uses GitHub's public API (no auth required for basic access).
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_base = "https://api.github.com"
    
    async def search_ai_repos(
        self,
        query: str = "AI OR LLM OR machine-learning",
        sort: str = "stars",
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search GitHub for AI-related repositories"""
        logger.info("Searching GitHub repos", query=query)
        
        try:
            # GitHub search API
            params = {
                "q": f"{query} language:python language:typescript",
                "sort": sort,
                "order": "desc",
                "per_page": limit,
            }
            
            headers = {
                "Accept": "application/vnd.github+json",
            }
            
            # Add auth if available
            if settings.GITHUB_TOKEN:
                headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
            
            response = await self.client.get(
                f"{self.api_base}/search/repositories",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            repos = []
            for repo in data.get("items", []):
                repos.append({
                    "source": "GitHub",
                    "source_type": "api",
                    "category": "tools",
                    "vertical": "devtools",
                    "title": repo["full_name"],
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "description": repo.get("description", "")[:500] if repo.get("description") else "",
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "topics": repo.get("topics", []),
                    "last_updated": repo.get("updated_at", ""),
                    "created_at": repo.get("created_at", ""),
                    "license": repo.get("license", {}).get("spdx_id", "") if repo.get("license") else "",
                    "open_issues": repo.get("open_issues_count", 0),
                    "is_archived": repo.get("archived", False),
                })
            
            logger.info("Found GitHub repos", count=len(repos))
            return repos
            
        except Exception as e:
            logger.error("GitHub search failed", error=str(e))
            return []
    
    async def get_trending_repos(self, language: str = None) -> List[Dict[str, Any]]:
        """Get trending repositories (scrape GitHub trending page)"""
        url = "https://github.com/trending"
        if language:
            url = f"https://github.com/trending/{language}"
        
        logger.info("Scraping GitHub trending", url=url)
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            repos = []
            
            for article in soup.select("article.Box-row"):
                try:
                    title_elem = article.select_one("h2 a")
                    if not title_elem:
                        continue
                    
                    full_name = title_elem.get("href", "").strip("/")
                    desc_elem = article.select_one("p")
                    stars_elem = article.select_one("span.d-inline-block.float-sm-right")
                    
                    repos.append({
                        "source": "GitHub Trending",
                        "source_type": "scrape",
                        "category": "tools",
                        "vertical": "devtools",
                        "title": full_name,
                        "name": full_name.split("/")[-1] if "/" in full_name else full_name,
                        "url": f"https://github.com/{full_name}",
                        "description": desc_elem.get_text(strip=True)[:500] if desc_elem else "",
                        "stars_today": self._parse_stars(stars_elem.get_text(strip=True) if stars_elem else "0"),
                    })
                except Exception as e:
                    logger.warning("Failed to parse trending repo", error=str(e))
                    continue
            
            logger.info("Found trending repos", count=len(repos))
            return repos
            
        except Exception as e:
            logger.error("GitHub trending scrape failed", error=str(e))
            return []
    
    def _parse_stars(self, text: str) -> int:
        """Parse stars count from text like '1,234 stars today'"""
        try:
            nums = re.findall(r"[\d,]+", text)
            if nums:
                return int(nums[0].replace(",", ""))
        except:
            pass
        return 0


# ===========================================
# HackerNews Scraper
# ===========================================

class HackerNewsScraper:
    """
    HackerNews API scraper for AI/ML discussions and tool launches.
    Uses the public HN Algolia API (self-hostable alternative available).
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_base = "https://hn.algolia.com/api/v1"
    
    async def search_stories(
        self,
        query: str = "AI LLM GPT Claude",
        tags: str = "story",
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search HackerNews stories"""
        logger.info("Searching HackerNews", query=query)
        
        try:
            params = {
                "query": query,
                "tags": tags,
                "hitsPerPage": limit,
            }
            
            response = await self.client.get(
                f"{self.api_base}/search_by_date",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            stories = []
            for hit in data.get("hits", []):
                stories.append({
                    "source": "HackerNews",
                    "source_type": "api",
                    "category": "news",
                    "vertical": "devtools",
                    "title": hit.get("title", ""),
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    "description": hit.get("story_text", "")[:500] if hit.get("story_text") else "",
                    "author": hit.get("author", ""),
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "published_at": hit.get("created_at", ""),
                    "hn_id": hit.get("objectID", ""),
                })
            
            logger.info("Found HackerNews stories", count=len(stories))
            return stories
            
        except Exception as e:
            logger.error("HackerNews search failed", error=str(e))
            return []
    
    async def get_front_page(self) -> List[Dict[str, Any]]:
        """Get current front page stories"""
        return await self.search_stories(
            query="",
            tags="front_page",
            limit=30,
        )


# ===========================================
# Product Hunt Scraper
# ===========================================

class ProductHuntScraper:
    """
    Product Hunt scraper for AI tool launches.
    Uses web scraping (no API key required).
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_ai_products(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Scrape AI products from Product Hunt"""
        url = "https://www.producthunt.com/topics/artificial-intelligence"
        logger.info("Scraping Product Hunt AI", url=url)
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            products = []
            
            # Product Hunt uses React, so we need to extract from script tags
            # This is a simplified version - production would use Playwright
            
            # Try to find product items
            for item in soup.select("[data-test='post-item']")[:limit]:
                try:
                    title = item.select_one("h3")
                    tagline = item.select_one("[data-test='tagline']")
                    link = item.select_one("a[href^='/posts/']")
                    votes = item.select_one("[data-test='vote-button'] span")
                    
                    if title and link:
                        products.append({
                            "source": "Product Hunt",
                            "source_type": "scrape",
                            "category": "tools",
                            "vertical": "general",
                            "title": title.get_text(strip=True),
                            "url": f"https://www.producthunt.com{link.get('href', '')}",
                            "description": tagline.get_text(strip=True) if tagline else "",
                            "votes": int(votes.get_text(strip=True)) if votes else 0,
                        })
                except Exception as e:
                    logger.warning("Failed to parse PH product", error=str(e))
                    continue
            
            logger.info("Found Product Hunt products", count=len(products))
            return products
            
        except Exception as e:
            logger.error("Product Hunt scrape failed", error=str(e))
            return []


# ===========================================
# SearXNG Search Service
# ===========================================

class SearXNGSearchService:
    """
    Self-hosted SearXNG metasearch engine integration.
    Aggregates results from multiple search engines.
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.SEARXNG_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search(
        self,
        query: str,
        categories: List[str] = None,
        engines: List[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search using SearXNG
        
        Categories: general, news, science, files, images, videos, it, social media
        """
        logger.info("SearXNG search", query=query, categories=categories)
        
        try:
            params = {
                "q": query,
                "format": "json",
                "safesearch": 1,
            }
            
            if categories:
                params["categories"] = ",".join(categories)
            
            if engines:
                params["engines"] = ",".join(engines)
            
            response = await self.client.get(
                f"{self.base_url}/search",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", [])[:limit]:
                results.append({
                    "source": "SearXNG",
                    "source_type": "search",
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("content", "")[:500] if item.get("content") else "",
                    "engine": item.get("engine", ""),
                    "category": item.get("category", ""),
                    "score": item.get("score", 0),
                    "published_at": item.get("publishedDate", ""),
                })
            
            logger.info("SearXNG results", count=len(results))
            return results
            
        except Exception as e:
            logger.error("SearXNG search failed", error=str(e))
            return []
    
    async def search_ai_news(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Search for latest AI news"""
        return await self.search(
            query="AI artificial intelligence machine learning LLM GPT",
            categories=["news"],
            limit=limit,
        )
    
    async def search_ai_tools(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Search for AI tools and products"""
        return await self.search(
            query="AI tool software platform machine learning",
            categories=["general", "it"],
            limit=limit,
        )


# ===========================================
# Unified Content Aggregator
# ===========================================

class ContentAggregator:
    """
    Unified content aggregator that combines all sources.
    Handles deduplication and normalization.
    """
    
    def __init__(self):
        self.rss_parser = RSSFeedParser()
        self.github_scraper = GitHubScraper()
        self.hn_scraper = HackerNewsScraper()
        self.ph_scraper = ProductHuntScraper()
        self.search_service = SearXNGSearchService()
    
    async def aggregate_news(self) -> List[Dict[str, Any]]:
        """Aggregate news from all sources"""
        logger.info("Aggregating news from all sources")
        
        tasks = [
            self.rss_parser.parse_all_feeds(),
            self.hn_scraper.search_stories(query="AI LLM GPT Claude Anthropic"),
            self.search_service.search_ai_news(limit=50),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
        
        logger.info("Aggregated news items", total=len(unique_items))
        return unique_items
    
    async def aggregate_tools(self) -> List[Dict[str, Any]]:
        """Aggregate tools from all sources"""
        logger.info("Aggregating tools from all sources")
        
        tasks = [
            self.github_scraper.get_trending_repos(),
            self.github_scraper.search_ai_repos(query="AI LLM agent framework", limit=50),
            self.ph_scraper.get_ai_products(limit=30),
            self.search_service.search_ai_tools(limit=30),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)
        
        logger.info("Aggregated tool items", total=len(unique_items))
        return unique_items
    
    async def aggregate_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate all content types"""
        news_task = self.aggregate_news()
        tools_task = self.aggregate_tools()
        
        news, tools = await asyncio.gather(news_task, tools_task)
        
        return {
            "news": news,
            "tools": tools,
        }
