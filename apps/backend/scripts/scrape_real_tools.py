#!/usr/bin/env python3
"""
Scrape REAL AI tools from known directories.
Uses direct HTTP requests to scrape actual AI tool listings.
"""
import asyncio
import sys
import os
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()


@dataclass
class AITool:
    """Discovered AI tool"""
    name: str
    url: str
    description: str
    source: str
    category: Optional[str] = None
    logo_url: Optional[str] = None
    pricing: Optional[str] = None
    discovered_at: str = None
    
    def __post_init__(self):
        if not self.discovered_at:
            self.discovered_at = datetime.now(timezone.utc).isoformat()


class AIToolDirectoryScraper:
    """Scrapes known AI tool directories"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        self.tools: List[AITool] = []
    
    async def scrape_all(self) -> List[AITool]:
        """Scrape all configured sources"""
        scrapers = [
            self.scrape_there_is_an_ai,
            self.scrape_toolify,
            self.scrape_ai_tool_directory,
        ]
        
        for scraper in scrapers:
            try:
                tools = await scraper()
                self.tools.extend(tools)
                logger.info(f"Scraped {len(tools)} tools from {scraper.__name__}")
            except Exception as e:
                logger.error(f"Failed to scrape {scraper.__name__}", error=str(e))
        
        # Dedupe by URL
        seen_urls = set()
        unique_tools = []
        for tool in self.tools:
            if tool.url not in seen_urls:
                seen_urls.add(tool.url)
                unique_tools.append(tool)
        
        return unique_tools

    async def scrape_there_is_an_ai(self) -> List[AITool]:
        """Scrape theresanaiforthat.com"""
        tools = []
        logger.info("Scraping theresanaiforthat.com...")
        
        try:
            # They have a public API-like JSON endpoint
            response = await self.client.get("https://theresanaiforthat.com/api/")
            if response.status_code != 200:
                # Fallback to HTML scraping
                response = await self.client.get("https://theresanaiforthat.com/")
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find tool cards
                for card in soup.select(".ai-card, .tool-card, [data-tool]")[:50]:
                    try:
                        name_el = card.select_one("h2, h3, .tool-name, .ai-name")
                        link_el = card.select_one("a[href*='/go/'], a[href*='http']")
                        desc_el = card.select_one("p, .description")
                        
                        if name_el and link_el:
                            url = link_el.get("href", "")
                            if url.startswith("/"):
                                url = f"https://theresanaiforthat.com{url}"
                            
                            tools.append(AITool(
                                name=name_el.get_text(strip=True),
                                url=url,
                                description=desc_el.get_text(strip=True) if desc_el else "",
                                source="theresanaiforthat.com",
                            ))
                    except Exception as e:
                        continue
        except Exception as e:
            logger.warning("TAAFT scrape failed", error=str(e))
        
        return tools

    async def scrape_toolify(self) -> List[AITool]:
        """Scrape toolify.ai for AI tools"""
        tools = []
        logger.info("Scraping toolify.ai...")
        
        try:
            # Toolify has a nice structure
            categories = ["productivity", "writing", "coding", "design", "marketing"]
            
            for category in categories:
                try:
                    response = await self.client.get(f"https://www.toolify.ai/{category}")
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        
                        # Find tool items
                        for item in soup.select("[class*='tool'], [class*='card'], article")[:20]:
                            try:
                                name_el = item.select_one("h2, h3, [class*='title'], [class*='name']")
                                link_el = item.select_one("a[href]")
                                desc_el = item.select_one("p, [class*='desc']")
                                
                                if name_el:
                                    name = name_el.get_text(strip=True)
                                    url = ""
                                    if link_el:
                                        href = link_el.get("href", "")
                                        if href.startswith("http"):
                                            url = href
                                        elif href.startswith("/"):
                                            url = f"https://www.toolify.ai{href}"
                                    
                                    if name and url:
                                        tools.append(AITool(
                                            name=name,
                                            url=url,
                                            description=desc_el.get_text(strip=True) if desc_el else "",
                                            source="toolify.ai",
                                            category=category,
                                        ))
                            except:
                                continue
                except:
                    continue
                    
                await asyncio.sleep(0.5)  # Be nice
                
        except Exception as e:
            logger.warning("Toolify scrape failed", error=str(e))
        
        return tools

    async def scrape_ai_tool_directory(self) -> List[AITool]:
        """Scrape aitoolsdirectory.com"""
        tools = []
        logger.info("Scraping AI tools directory...")
        
        try:
            response = await self.client.get("https://www.aitoolsdirectory.com/")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                for item in soup.select("[class*='tool'], [class*='card'], .item")[:30]:
                    try:
                        name_el = item.select_one("h2, h3, .name, .title")
                        link_el = item.select_one("a[href]")
                        desc_el = item.select_one("p, .description")
                        
                        if name_el and link_el:
                            href = link_el.get("href", "")
                            if href.startswith("/"):
                                href = f"https://www.aitoolsdirectory.com{href}"
                            
                            tools.append(AITool(
                                name=name_el.get_text(strip=True),
                                url=href,
                                description=desc_el.get_text(strip=True) if desc_el else "",
                                source="aitoolsdirectory.com",
                            ))
                    except:
                        continue
        except Exception as e:
            logger.warning("AI Tools Directory scrape failed", error=str(e))
        
        return tools

    async def close(self):
        await self.client.aclose()


# ============================================
# Known AI Tools (curated list)
# ============================================

CURATED_AI_TOOLS = [
    # Writing & Content
    AITool(name="Jasper", url="https://www.jasper.ai", description="AI-powered writing assistant for marketing teams", source="curated", category="writing"),
    AITool(name="Copy.ai", url="https://www.copy.ai", description="AI copywriting tool for marketing content", source="curated", category="writing"),
    AITool(name="Writesonic", url="https://writesonic.com", description="AI writer for blogs, ads, and marketing content", source="curated", category="writing"),
    AITool(name="Rytr", url="https://rytr.me", description="AI writing assistant for creating content", source="curated", category="writing"),
    AITool(name="Sudowrite", url="https://www.sudowrite.com", description="AI writing partner for fiction authors", source="curated", category="writing"),
    
    # Code & Development
    AITool(name="Cursor", url="https://cursor.com", description="AI-first code editor with native AI integration", source="curated", category="devtools"),
    AITool(name="Tabnine", url="https://www.tabnine.com", description="AI code completion for developers", source="curated", category="devtools"),
    AITool(name="Codeium", url="https://codeium.com", description="Free AI-powered code completion", source="curated", category="devtools"),
    AITool(name="Replit", url="https://replit.com", description="AI-powered collaborative coding platform", source="curated", category="devtools"),
    AITool(name="v0", url="https://v0.dev", description="AI UI component generator by Vercel", source="curated", category="devtools"),
    AITool(name="Bolt", url="https://bolt.new", description="AI full-stack web app builder", source="curated", category="devtools"),
    
    # Image & Design
    AITool(name="Midjourney", url="https://www.midjourney.com", description="AI image generation from text prompts", source="curated", category="image"),
    AITool(name="DALL-E", url="https://openai.com/dall-e-3", description="AI image generation by OpenAI", source="curated", category="image"),
    AITool(name="Leonardo AI", url="https://leonardo.ai", description="AI image generation for creative professionals", source="curated", category="image"),
    AITool(name="Ideogram", url="https://ideogram.ai", description="AI image generator with excellent text rendering", source="curated", category="image"),
    AITool(name="Canva Magic", url="https://www.canva.com/magic-design/", description="AI design tools integrated into Canva", source="curated", category="design"),
    AITool(name="Figma AI", url="https://www.figma.com/ai/", description="AI-powered design features in Figma", source="curated", category="design"),
    
    # Video & Audio
    AITool(name="Runway", url="https://runwayml.com", description="AI video generation and editing tools", source="curated", category="video"),
    AITool(name="Synthesia", url="https://www.synthesia.io", description="AI video generation with avatars", source="curated", category="video"),
    AITool(name="Descript", url="https://www.descript.com", description="AI-powered audio and video editing", source="curated", category="video"),
    AITool(name="ElevenLabs", url="https://elevenlabs.io", description="AI voice synthesis and cloning", source="curated", category="audio"),
    AITool(name="Murf AI", url="https://murf.ai", description="AI voice generator for voiceovers", source="curated", category="audio"),
    
    # Productivity
    AITool(name="Notion AI", url="https://www.notion.so/product/ai", description="AI assistant integrated into Notion", source="curated", category="productivity"),
    AITool(name="Otter.ai", url="https://otter.ai", description="AI meeting transcription and notes", source="curated", category="productivity"),
    AITool(name="Fireflies.ai", url="https://fireflies.ai", description="AI meeting assistant with transcription", source="curated", category="productivity"),
    AITool(name="Mem", url="https://get.mem.ai", description="AI-powered note-taking and knowledge base", source="curated", category="productivity"),
    AITool(name="Motion", url="https://www.usemotion.com", description="AI calendar and task management", source="curated", category="productivity"),
    
    # Research & Analysis
    AITool(name="Perplexity", url="https://www.perplexity.ai", description="AI-powered research and answer engine", source="curated", category="research"),
    AITool(name="Elicit", url="https://elicit.com", description="AI research assistant for academic papers", source="curated", category="research"),
    AITool(name="Consensus", url="https://consensus.app", description="AI search engine for scientific research", source="curated", category="research"),
    AITool(name="Semantic Scholar", url="https://www.semanticscholar.org", description="AI-powered academic search engine", source="curated", category="research"),
    
    # Customer Support
    AITool(name="Intercom Fin", url="https://www.intercom.com/fin", description="AI customer support chatbot", source="curated", category="support"),
    AITool(name="Ada", url="https://www.ada.cx", description="AI-powered customer service automation", source="curated", category="support"),
    AITool(name="Zendesk AI", url="https://www.zendesk.com/service/ai/", description="AI features for customer service", source="curated", category="support"),
    
    # Marketing
    AITool(name="Persado", url="https://www.persado.com", description="AI-powered marketing language optimization", source="curated", category="marketing"),
    AITool(name="Phrasee", url="https://phrasee.co", description="AI copywriting for enterprise marketing", source="curated", category="marketing"),
    AITool(name="Surfer SEO", url="https://surferseo.com", description="AI-powered SEO content optimization", source="curated", category="marketing"),
    
    # Data & Analytics  
    AITool(name="Obviously AI", url="https://www.obviously.ai", description="No-code AI for predictive analytics", source="curated", category="data"),
    AITool(name="MonkeyLearn", url="https://monkeylearn.com", description="AI text analysis and classification", source="curated", category="data"),
]


async def process_tools(tools: List[AITool], limit: int = 20):
    """Process discovered tools through the pipeline"""
    from app.services.publisher import MDXPublisher
    from app.models import ToolData, ToolPricing, WrapperStatus, Vertical, PricingType
    
    publisher = MDXPublisher()
    processed = 0
    
    for tool in tools[:limit]:
        try:
            # Create basic tool data
            slug = re.sub(r'[^a-z0-9]+', '-', tool.name.lower()).strip('-')
            
            # Map category to vertical (using actual enum values: agtech, legal, devtools, marketing, healthcare, finance, general)
            category_to_vertical = {
                "writing": Vertical.MARKETING,
                "devtools": Vertical.DEVTOOLS,
                "image": Vertical.GENERAL,
                "design": Vertical.GENERAL,
                "video": Vertical.GENERAL,
                "audio": Vertical.GENERAL,
                "productivity": Vertical.GENERAL,
                "research": Vertical.GENERAL,  # No education vertical
                "support": Vertical.GENERAL,
                "marketing": Vertical.MARKETING,
                "data": Vertical.FINANCE,
            }
            vertical = category_to_vertical.get(tool.category, Vertical.GENERAL)
            
            tool_data = ToolData(
                name=tool.name,
                slug=slug,
                description=tool.description,
                url=tool.url,
                logo_url=f"/images/tools/{slug}.png",
                vertical=vertical,
                categories=[tool.category or "general"],
                tags=["ai", tool.category or "tool"],
                trust_score=70,  # Default score, to be updated by Trust Engine
                wrapper_status=WrapperStatus.UNKNOWN,
                is_verified=False,
                pricing=ToolPricing(type=PricingType.FREEMIUM),
                content=f"**{tool.name}** - {tool.description}\n\nVisit [{tool.name}]({tool.url}) to learn more.",
                source=tool.source,
                source_url=tool.url,
            )
            
            # Publish to MDX
            file_path = publisher.publish_tool(tool_data)
            logger.info("Published tool", name=tool.name, path=file_path)
            processed += 1
            
        except Exception as e:
            logger.error("Failed to process tool", name=tool.name, error=str(e))
    
    return processed


async def main():
    """Main discovery and processing"""
    logger.info("Starting AI tool discovery from directories")
    
    # Start with curated list
    all_tools = list(CURATED_AI_TOOLS)
    logger.info(f"Loaded {len(all_tools)} curated tools")
    
    # Add scraped tools
    if len(sys.argv) > 1 and sys.argv[1] == "--scrape":
        scraper = AIToolDirectoryScraper()
        try:
            scraped_tools = await scraper.scrape_all()
            all_tools.extend(scraped_tools)
            logger.info(f"Scraped {len(scraped_tools)} additional tools")
        finally:
            await scraper.close()
    
    # Print tools
    print("\n" + "="*70)
    print("DISCOVERED AI TOOLS")
    print("="*70)
    
    for i, tool in enumerate(all_tools[:50], 1):
        print(f"\n{i}. {tool.name}")
        print(f"   URL: {tool.url}")
        print(f"   Category: {tool.category or 'general'}")
        print(f"   Source: {tool.source}")
        if tool.description:
            print(f"   {tool.description[:80]}...")
    
    print(f"\n{'='*70}")
    print(f"Total tools: {len(all_tools)}")
    print("="*70)
    
    # Process tools
    if len(sys.argv) > 1 and "--process" in sys.argv:
        idx = sys.argv.index("--process")
        limit = int(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else 20
        print(f"\nProcessing top {limit} tools...")
        processed = await process_tools(all_tools, limit=limit)
        print(f"✅ Published {processed} tools to frontend")
    else:
        print("\nRun with --process [N] to publish top N tools to frontend")
        print("Run with --scrape to also scrape online directories")


if __name__ == "__main__":
    asyncio.run(main())

