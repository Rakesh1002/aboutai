"""
Scrapers for startup launch sites and AI tool directories.
Uses Playwright for JavaScript-rendered sites.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import structlog
import asyncio
import re
import json

from app.agents.scraper.browser import browser_pool, scrape_with_browser

logger = structlog.get_logger()


@dataclass
class LaunchItem:
    """Normalized launch/tool item from any source"""
    source: str
    title: str
    url: str
    description: str
    logo_url: Optional[str] = None
    category: str = "tools"
    vertical: str = "general"
    votes: int = 0
    comments: int = 0
    launched_at: Optional[str] = None
    tags: List[str] = None
    extra: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.extra is None:
            self.extra = {}


class ProductHuntScraper:
    """
    Scraper for Product Hunt using RSS feed (more reliable than browser).
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.rss_url = "https://www.producthunt.com/feed"
    
    async def get_ai_launches(self, limit: int = 30) -> List[LaunchItem]:
        """Get recent launches from Product Hunt RSS feed, filter for AI"""
        logger.info("Scraping Product Hunt via RSS feed")
        
        items = []
        ai_keywords = [
            'ai', 'gpt', 'llm', 'chatgpt', 'claude', 'openai', 'anthropic',
            'machine learning', 'neural', 'automation', 'copilot', 'assistant',
            'generative', 'prompt', 'agent', 'workflow', 'productivity',
        ]
        
        try:
            # Try RSS feed first
            response = await self.client.get(self.rss_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'xml')
            entries = soup.find_all('item')
            
            logger.info("Found RSS entries", count=len(entries))
            
            for entry in entries:
                try:
                    title = entry.find('title').text if entry.find('title') else ""
                    link = entry.find('link').text if entry.find('link') else ""
                    description = entry.find('description').text if entry.find('description') else ""
                    
                    # Clean description (remove HTML)
                    if description:
                        desc_soup = BeautifulSoup(description, 'html.parser')
                        description = desc_soup.get_text()[:500]
                    
                    # Check if AI-related
                    text_to_check = f"{title} {description}".lower()
                    is_ai = any(kw in text_to_check for kw in ai_keywords)
                    
                    if title and link and is_ai:
                        items.append(LaunchItem(
                            source="Product Hunt",
                            title=title[:200],
                            url=link,
                            description=description,
                            category="tools",
                            vertical="ai",
                        ))
                except Exception as e:
                    logger.debug("Failed to parse RSS entry", error=str(e))
                    continue
            
            # If RSS didn't work, try API endpoint
            if len(items) < 5:
                items.extend(await self._scrape_api())
                
        except Exception as e:
            logger.warning("RSS scrape failed, trying API", error=str(e))
            items = await self._scrape_api()
        
        logger.info("Found Product Hunt launches", count=len(items))
        return items[:limit]
    
    async def _scrape_api(self) -> List[LaunchItem]:
        """Try to get data from ProductHunt's public API endpoints"""
        items = []
        
        try:
            # ProductHunt has a public endpoint for today's products
            response = await self.client.get(
                "https://api.producthunt.com/v2/api/graphql",
                headers={"Accept": "application/json"}
            )
            
            # If that fails, try the homepage and parse it
            if response.status_code != 200:
                response = await self.client.get("https://www.producthunt.com/")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for product cards in the HTML
                scripts = soup.find_all('script', type='application/json')
                for script in scripts:
                    try:
                        data = json.loads(script.string or "{}")
                        # Extract products from JSON data
                        if isinstance(data, dict):
                            products = self._extract_products(data)
                            items.extend(products)
                    except:
                        continue
                        
        except Exception as e:
            logger.error("API scrape failed", error=str(e))
        
        return items
    
    def _extract_products(self, data: dict, depth: int = 0) -> List[LaunchItem]:
        """Recursively extract products from nested JSON"""
        items = []
        if depth > 5:
            return items
            
        if isinstance(data, dict):
            # Check if this looks like a product
            if 'name' in data and 'tagline' in data:
                url = data.get('url') or data.get('website') or ""
                if url:
                    items.append(LaunchItem(
                        source="Product Hunt",
                        title=data.get('name', '')[:200],
                        url=url,
                        description=data.get('tagline', '')[:500],
                        votes=data.get('votesCount', 0),
                        category="tools",
                        vertical="ai",
                    ))
            
            # Recurse into nested dicts
            for value in data.values():
                items.extend(self._extract_products(value, depth + 1))
                
        elif isinstance(data, list):
            for item in data[:50]:  # Limit to prevent infinite loops
                items.extend(self._extract_products(item, depth + 1))
        
        return items


class HackerNewsScraper:
    """
    Scraper for Hacker News - great source for AI tools.
    Uses simple HTTP since HN is server-rendered.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "https://news.ycombinator.com"
    
    async def get_ai_posts(self, limit: int = 30) -> List[LaunchItem]:
        """Get AI-related posts from Hacker News front page and Show HN"""
        logger.info("Scraping Hacker News for AI content")
        
        items = []
        ai_keywords = [
            'ai', 'gpt', 'llm', 'chatgpt', 'claude', 'openai', 'anthropic',
            'machine learning', 'neural', 'transformer', 'diffusion',
            'copilot', 'gemini', 'mistral', 'llama', 'artificial intelligence'
        ]
        
        try:
            # Scrape front page and Show HN
            urls = [
                f"{self.base_url}/news",
                f"{self.base_url}/show",
                f"{self.base_url}/newest",
            ]
            
            for url in urls:
                response = await self.client.get(url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # HN structure: tr.athing contains title, next tr contains subtext
                for row in soup.select('tr.athing'):
                    try:
                        title_cell = row.select_one('td.title')
                        if not title_cell:
                            continue
                        
                        link = title_cell.select_one('a.titleline > a, span.titleline > a')
                        if not link:
                            continue
                        
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        # Check if AI-related
                        title_lower = title.lower()
                        if not any(kw in title_lower for kw in ai_keywords):
                            continue
                        
                        # Handle relative URLs
                        if href.startswith('item?'):
                            href = f"{self.base_url}/{href}"
                        
                        # Get score from next row
                        score = 0
                        subtext = row.find_next_sibling('tr')
                        if subtext:
                            score_el = subtext.select_one('span.score')
                            if score_el:
                                score_text = score_el.get_text()
                                score = int(re.sub(r'\D', '', score_text) or 0)
                        
                        items.append(LaunchItem(
                            source="Hacker News",
                            title=title[:200],
                            url=href,
                            description="",
                            votes=score,
                            category="tools",
                            vertical="ai",
                        ))
                    except Exception as e:
                        continue
                
                await asyncio.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            logger.error("HN scrape failed", error=str(e))
        
        # Deduplicate by URL
        seen = set()
        unique = []
        for item in items:
            if item.url not in seen:
                seen.add(item.url)
                unique.append(item)
        
        logger.info("Found Hacker News AI posts", count=len(unique))
        return unique[:limit]


class GitHubTrendingScraper:
    """
    Scraper for GitHub Trending repositories.
    Great source for new AI tools and libraries.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_trending_ai_repos(self, limit: int = 30) -> List[LaunchItem]:
        """Get trending AI-related repositories"""
        logger.info("Scraping GitHub Trending for AI repos")
        
        items = []
        
        try:
            # Trending page for different time ranges
            urls = [
                "https://github.com/trending?since=daily",
                "https://github.com/trending?since=weekly",
                "https://github.com/trending/python?since=daily",
            ]
            
            ai_keywords = [
                'ai', 'gpt', 'llm', 'ml', 'neural', 'transformer',
                'diffusion', 'langchain', 'openai', 'anthropic',
                'machine-learning', 'deep-learning', 'nlp', 'chatbot'
            ]
            
            for url in urls:
                response = await self.client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for article in soup.select('article.Box-row'):
                    try:
                        # Get repo link
                        link = article.select_one('h2 a')
                        if not link:
                            continue
                        
                        href = link.get('href', '')
                        repo_name = href.strip('/')
                        
                        # Get description
                        desc_el = article.select_one('p')
                        description = desc_el.get_text(strip=True) if desc_el else ""
                        
                        # Check if AI-related
                        text = f"{repo_name} {description}".lower()
                        if not any(kw in text for kw in ai_keywords):
                            continue
                        
                        # Get stars
                        stars = 0
                        star_el = article.select_one('a[href*="/stargazers"]')
                        if star_el:
                            star_text = star_el.get_text(strip=True).replace(',', '')
                            stars = int(re.sub(r'\D', '', star_text) or 0)
                        
                        items.append(LaunchItem(
                            source="GitHub",
                            title=repo_name,
                            url=f"https://github.com{href}",
                            description=description[:500],
                            votes=stars,
                            category="tools",
                            vertical="ai",
                        ))
                    except Exception as e:
                        continue
                
                await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error("GitHub trending scrape failed", error=str(e))
        
        # Deduplicate
        seen = set()
        unique = []
        for item in items:
            if item.url not in seen:
                seen.add(item.url)
                unique.append(item)
        
        logger.info("Found GitHub trending AI repos", count=len(unique))
        return unique[:limit]


class AIDirectoryScraper:
    """
    Scraper for AI tool directories using Playwright.
    Handles: Futurepedia, There's An AI For That, etc.
    """
    
    async def scrape_futurepedia(self, limit: int = 30) -> List[LaunchItem]:
        """Scrape Futurepedia AI tools directory"""
        logger.info("Scraping Futurepedia with browser")
        
        items = []
        
        try:
            async with browser_pool.get_page() as page:
                await page.goto(
                    "https://www.futurepedia.io/ai-tools",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                
                await asyncio.sleep(2)
                
                # Scroll to load content
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(0.5)
                
                # Find tool cards
                cards = await page.query_selector_all('[class*="tool"], [class*="card"], article')
                
                logger.info("Found Futurepedia elements", count=len(cards))
                
                for card in cards[:limit]:
                    try:
                        link = await card.query_selector('a[href*="/tool/"], a[href*="/ai-tools/"]')
                        if not link:
                            link = await card.query_selector('a')
                        
                        if not link:
                            continue
                        
                        href = await link.get_attribute('href')
                        if not href:
                            continue
                        
                        if href.startswith('/'):
                            href = f"https://www.futurepedia.io{href}"
                        
                        title_el = await card.query_selector('h2, h3, [class*="title"], [class*="name"]')
                        title = await title_el.inner_text() if title_el else ""
                        
                        desc_el = await card.query_selector('p, [class*="description"]')
                        description = await desc_el.inner_text() if desc_el else ""
                        
                        if title:
                            items.append(LaunchItem(
                                source="Futurepedia",
                                title=title[:200],
                                url=href,
                                description=description[:500],
                                category="tools",
                                vertical="ai",
                            ))
                    except:
                        continue
                        
        except Exception as e:
            logger.error("Futurepedia scrape failed", error=str(e))
        
        logger.info("Found Futurepedia tools", count=len(items))
        return items
    
    async def scrape_taaft(self, limit: int = 30) -> List[LaunchItem]:
        """Scrape There's An AI For That directory"""
        logger.info("Scraping TAAFT with browser")
        
        items = []
        
        try:
            async with browser_pool.get_page() as page:
                await page.goto(
                    "https://theresanaiforthat.com/",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                
                await asyncio.sleep(2)
                
                # Scroll to load content
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(0.5)
                
                # Find AI tool cards
                cards = await page.query_selector_all('[class*="ai"], [class*="tool"], article, .card')
                
                logger.info("Found TAAFT elements", count=len(cards))
                
                for card in cards[:limit]:
                    try:
                        link = await card.query_selector('a')
                        if not link:
                            continue
                        
                        href = await link.get_attribute('href')
                        if not href or href == '#':
                            continue
                        
                        if href.startswith('/'):
                            href = f"https://theresanaiforthat.com{href}"
                        
                        # Skip non-tool links
                        if 'theresanaiforthat.com' not in href and not href.startswith('http'):
                            continue
                        
                        title_el = await card.query_selector('h2, h3, h4, [class*="title"], [class*="name"], strong')
                        title = await title_el.inner_text() if title_el else ""
                        
                        desc_el = await card.query_selector('p, [class*="description"], [class*="summary"]')
                        description = await desc_el.inner_text() if desc_el else ""
                        
                        if title and len(title) > 2:
                            items.append(LaunchItem(
                                source="There's An AI For That",
                                title=title[:200],
                                url=href,
                                description=description[:500],
                                category="tools",
                                vertical="ai",
                            ))
                    except:
                        continue
                        
        except Exception as e:
            logger.error("TAAFT scrape failed", error=str(e))
        
        logger.info("Found TAAFT tools", count=len(items))
        return items


class BetaListScraper:
    """Scraper for BetaList using browser automation"""
    
    async def get_ai_startups(self, limit: int = 30) -> List[LaunchItem]:
        """Get AI-related startups from BetaList"""
        logger.info("Scraping BetaList with browser")
        
        items = []
        
        try:
            async with browser_pool.get_page() as page:
                await page.goto(
                    "https://betalist.com/topics/artificial-intelligence",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                
                await asyncio.sleep(2)
                
                # Scroll to load content
                for _ in range(2):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(0.5)
                
                # Find startup cards
                cards = await page.query_selector_all('article, [class*="startup"], [class*="card"]')
                
                logger.info("Found BetaList elements", count=len(cards))
                
                for card in cards[:limit]:
                    try:
                        link = await card.query_selector('a[href*="/startups/"], a')
                        if not link:
                            continue
                        
                        href = await link.get_attribute('href')
                        if not href:
                            continue
                        
                        if href.startswith('/'):
                            href = f"https://betalist.com{href}"
                        
                        title_el = await card.query_selector('h2, h3, [class*="title"], [class*="name"]')
                        title = await title_el.inner_text() if title_el else ""
                        
                        desc_el = await card.query_selector('p, [class*="description"]')
                        description = await desc_el.inner_text() if desc_el else ""
                        
                        if title:
                            items.append(LaunchItem(
                                source="BetaList",
                                title=title[:200],
                                url=href,
                                description=description[:500],
                                category="tools",
                                vertical="ai",
                            ))
                    except:
                        continue
                        
        except Exception as e:
            logger.error("BetaList scrape failed", error=str(e))
        
        logger.info("Found BetaList startups", count=len(items))
        return items


# ===========================================
# Unified Launch Site Aggregator
# ===========================================

class LaunchSiteAggregator:
    """
    Aggregates tool launches from all startup/AI directories.
    """
    
    def __init__(self):
        self.ph_scraper = ProductHuntScraper()
        self.hn_scraper = HackerNewsScraper()
        self.gh_scraper = GitHubTrendingScraper()
        self.ai_scraper = AIDirectoryScraper()
        self.betalist_scraper = BetaListScraper()
    
    async def aggregate_all_launches(self, limit_per_source: int = 20) -> List[LaunchItem]:
        """
        Aggregate launches from all sources.
        Returns deduplicated list sorted by relevance.
        """
        logger.info("Aggregating launches from all sources")
        
        all_items = []
        
        # Run scrapers with error handling
        # Start with faster HTTP-based scrapers
        scrapers = [
            ("Hacker News", self.hn_scraper.get_ai_posts(limit_per_source)),
            ("GitHub", self.gh_scraper.get_trending_ai_repos(limit_per_source)),
        ]
        
        # Run fast scrapers in parallel
        fast_results = await asyncio.gather(
            *[s[1] for s in scrapers],
            return_exceptions=True
        )
        
        for (name, _), result in zip(scrapers, fast_results):
            if isinstance(result, Exception):
                logger.warning(f"{name} scraper failed", error=str(result))
            elif result:
                all_items.extend(result)
                logger.info(f"{name} returned items", count=len(result))
        
        # Run browser-based scrapers sequentially to avoid resource contention
        browser_scrapers = [
            ("Product Hunt", self.ph_scraper.get_ai_launches),
            ("Futurepedia", self.ai_scraper.scrape_futurepedia),
            ("TAAFT", self.ai_scraper.scrape_taaft),
            ("BetaList", self.betalist_scraper.get_ai_startups),
        ]
        
        for name, scraper_func in browser_scrapers:
            try:
                result = await scraper_func(limit_per_source)
                if result:
                    all_items.extend(result)
                    logger.info(f"{name} returned items", count=len(result))
            except Exception as e:
                logger.warning(f"{name} scraper failed", error=str(e))
        
        # Deduplicate by normalized URL
        seen = set()
        unique = []
        for item in all_items:
            normalized_url = self._normalize_url(item.url)
            if normalized_url not in seen and item.title:
                seen.add(normalized_url)
                unique.append(item)
        
        # Sort by votes and source priority
        source_priority = {
            "Product Hunt": 1,
            "Hacker News": 1,
            "GitHub": 2,
            "BetaList": 3,
            "Futurepedia": 4,
            "There's An AI For That": 4,
        }
        
        unique.sort(key=lambda x: (
            source_priority.get(x.source, 5),
            -x.votes,
        ))
        
        logger.info("Aggregated unique launches", count=len(unique))
        return unique
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        url = url.lower().strip()
        url = re.sub(r"^https?://", "", url)
        url = re.sub(r"^www\.", "", url)
        url = url.rstrip("/")
        # Remove query params for dedup
        url = url.split('?')[0]
        return url
