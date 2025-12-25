"""
Browser automation utilities using Playwright.
Handles JavaScript-rendered sites that block simple HTTP requests.
"""
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import structlog
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logger = structlog.get_logger()


class BrowserPool:
    """
    Manages a pool of browser instances for efficient scraping.
    Reuses browser contexts to avoid repeated startup costs.
    """
    
    _instance: Optional["BrowserPool"] = None
    _browser: Optional[Browser] = None
    _playwright = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_browser(self) -> Browser:
        """Get or create browser instance"""
        if self._browser is None or not self._browser.is_connected():
            await self._init_browser()
        return self._browser
    
    async def _init_browser(self):
        """Initialize Playwright and browser"""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--window-size=1920,1080",
            ]
        )
        logger.info("Browser initialized")
    
    @asynccontextmanager
    async def get_page(self, stealth: bool = True):
        """Get a new page with optional stealth mode"""
        browser = await self.get_browser()
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        if stealth:
            # Add stealth scripts to avoid detection
            await context.add_init_script("""
                // Overwrite navigator properties
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                
                // Mock chrome object
                window.chrome = { runtime: {} };
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
        
        page = await context.new_page()
        
        try:
            yield page
        finally:
            await page.close()
            await context.close()
    
    async def close(self):
        """Close browser and cleanup"""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None


# Global browser pool instance
browser_pool = BrowserPool()


async def scrape_with_browser(
    url: str,
    wait_for: str = "networkidle",
    timeout: int = 30000,
    scroll: bool = True,
) -> str:
    """
    Scrape a URL using Playwright browser.
    
    Args:
        url: URL to scrape
        wait_for: Wait condition (networkidle, domcontentloaded, load)
        timeout: Timeout in milliseconds
        scroll: Whether to scroll to load lazy content
        
    Returns:
        HTML content of the page
    """
    async with browser_pool.get_page() as page:
        try:
            await page.goto(url, wait_until=wait_for, timeout=timeout)
            
            if scroll:
                # Scroll to load lazy content
                await _scroll_page(page)
            
            # Wait a bit for any final renders
            await asyncio.sleep(1)
            
            return await page.content()
            
        except Exception as e:
            logger.error("Browser scrape failed", url=url, error=str(e))
            raise


async def _scroll_page(page: Page, scroll_delay: float = 0.5):
    """Scroll page to trigger lazy loading"""
    try:
        # Get page height
        scroll_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        
        current = 0
        while current < scroll_height:
            current += viewport_height
            await page.evaluate(f"window.scrollTo(0, {current})")
            await asyncio.sleep(scroll_delay)
            
            # Check if page grew (infinite scroll)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height > scroll_height:
                scroll_height = new_height
                
            # Safety limit
            if current > 10000:
                break
        
        # Scroll back to top
        await page.evaluate("window.scrollTo(0, 0)")
        
    except Exception as e:
        logger.warning("Scroll failed", error=str(e))


async def extract_elements(
    page: Page,
    selector: str,
    attributes: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract elements from page matching selector.
    
    Args:
        page: Playwright page
        selector: CSS selector
        attributes: List of attributes to extract (default: href, text)
        
    Returns:
        List of dicts with extracted data
    """
    if attributes is None:
        attributes = ["href", "text"]
    
    elements = await page.query_selector_all(selector)
    results = []
    
    for el in elements:
        data = {}
        for attr in attributes:
            if attr == "text":
                data["text"] = await el.inner_text()
            elif attr == "html":
                data["html"] = await el.inner_html()
            else:
                data[attr] = await el.get_attribute(attr)
        results.append(data)
    
    return results
