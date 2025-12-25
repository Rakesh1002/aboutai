#!/usr/bin/env python3
"""
Discover and process AI tools using SearXNG.
This script finds real AI tools and processes them through the pipeline.
"""
import asyncio
import sys
import os

# Add the app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import structlog
from datetime import datetime
from typing import List, Dict, Any

logger = structlog.get_logger()

# URLs that should NOT be processed as AI tools
EXCLUDED_DOMAINS = [
    # Code repos
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    # Q&A and social
    "stackoverflow.com",
    "stackexchange.com",
    "medium.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "wikipedia.org",
    "reddit.com",
    "news.ycombinator.com",
    "quora.com",
    # Documentation sites
    "developer.mozilla.org",
    "docs.microsoft.com",
    "learn.microsoft.com",
    "developer.apple.com",
    "developers.google.com",
    "docs.aws.amazon.com",
    # Container registries
    "hub.docker.com",
    "gcr.io",
    "ghcr.io",
    # Package managers
    "pypi.org",
    "npmjs.com",
    "rubygems.org",
    # Aggregator sites (we want the actual tools, not lists)
    "topai.tools",
    "aitoolinsight.com",
    "futuretools.io",
    "futurepedia.io",
    "theresanaiforthat.com",
    "producthunt.com",  # We'll scrape PH separately
    "alternativeto.net",
    "g2.com",
    "capterra.com",
]

# AI tool indicators - URLs that are likely actual AI tools
AI_TOOL_INDICATORS = [
    ".ai",
    "ai.",
    "-ai.",
    "gpt",
    "chat",
    "copilot",
    "assistant",
    "automation",
]


async def search_searxng(query: str, limit: int = 30) -> List[Dict[str, Any]]:
    """Search using local SearXNG instance"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                "http://localhost:8080/search",
                params={
                    "q": query,
                    "format": "json",
                    "categories": "it",
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])[:limit]
        except Exception as e:
            logger.error("SearXNG search failed", error=str(e))
            return []


def is_valid_tool_url(url: str) -> bool:
    """Check if URL is likely a real AI tool (not a repo or aggregator)"""
    url_lower = url.lower()
    
    # Exclude known non-tool domains
    for excluded in EXCLUDED_DOMAINS:
        if excluded in url_lower:
            return False
    
    return True


def score_tool_likelihood(result: Dict[str, Any]) -> float:
    """Score how likely this is an actual AI tool vs. a blog/list"""
    score = 0.3  # Start lower, require positive signals
    
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()
    content = result.get("content", "").lower()
    
    # Strong boost for AI-related domain TLDs
    if url.endswith(".ai") or ".ai/" in url:
        score += 0.25
    
    # Boost for AI-related domain names
    for indicator in AI_TOOL_INDICATORS:
        if indicator in url:
            score += 0.1
    
    # Strong boost for product-like pages
    if any(word in url for word in ["pricing", "features", "/app", "/tool", "/product"]):
        score += 0.15
    
    # Boost for landing page (short path = likely main product page)
    url_path = url.split("//")[-1].split("/")
    if len(url_path) <= 2:  # domain + maybe one path segment
        score += 0.1
    
    # Penalize list/comparison pages heavily
    if any(word in title for word in ["best", "top 10", "top 20", "list of", "compare", "alternative", "vs ", " vs "]):
        score -= 0.4
    
    # Penalize blog/news/article pages
    if any(word in url for word in ["/blog/", "/article/", "/post/", "/news/", "/guide/", "/review/", "/tutorial/"]):
        score -= 0.3
    
    # Boost for clear product CTAs
    cta_keywords = ["try free", "sign up", "get started", "start free", "free trial", "pricing", "demo", "request access"]
    for cta in cta_keywords:
        if cta in content:
            score += 0.1
            break
    
    # Boost for SaaS/product indicators in content
    product_indicators = ["api", "integration", "dashboard", "workspace", "team", "enterprise", "pro plan", "monthly", "per month"]
    matches = sum(1 for p in product_indicators if p in content)
    score += min(matches * 0.05, 0.15)
    
    return min(max(score, 0.0), 1.0)


async def discover_ai_tools() -> List[Dict[str, Any]]:
    """Discover AI tools using multiple search queries"""
    
    # More specific queries targeting actual AI product sites
    queries = [
        "site:.ai AI assistant pricing",
        "site:.io AI tool free trial",
        "AI writing tool sign up free",
        "AI code completion tool pricing plans",
        "AI image generator online free",
        "AI chatbot platform enterprise",
        "AI meeting assistant tool",
        "AI research assistant tool",
        "AI email assistant chrome extension",
        "AI voice generator tool online",
        "AI transcription tool pricing",
        "AI presentation maker tool",
        "AI design tool figma alternative",
        "AI customer support chatbot saas",
    ]
    
    all_tools = []
    seen_urls = set()
    
    for query in queries:
        logger.info("Searching for AI tools", query=query)
        results = await search_searxng(query, limit=20)
        
        for result in results:
            url = result.get("url", "")
            if not url or url in seen_urls:
                continue
            
            seen_urls.add(url)
            
            # Filter out non-tool URLs
            if not is_valid_tool_url(url):
                logger.debug("Skipping non-tool URL", url=url)
                continue
            
            # Score the likelihood this is an actual tool
            tool_score = score_tool_likelihood(result)
            
            if tool_score >= 0.4:  # Only include likely tools
                all_tools.append({
                    "title": result.get("title", ""),
                    "url": url,
                    "description": result.get("content", ""),
                    "source": result.get("engine", "searxng"),
                    "tool_score": tool_score,
                    "discovered_at": datetime.utcnow().isoformat(),
                })
                logger.info("Found potential AI tool", 
                           title=result.get("title", "")[:50],
                           url=url[:50],
                           score=tool_score)
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    # Sort by tool score
    all_tools.sort(key=lambda x: x["tool_score"], reverse=True)
    
    return all_tools


async def process_discovered_tools(tools: List[Dict[str, Any]], limit: int = 10):
    """Process discovered tools through the pipeline"""
    from app.tasks.pipeline_tasks import process_single_tool_url
    
    processed = 0
    for tool in tools[:limit]:
        try:
            logger.info("Processing tool", title=tool["title"], url=tool["url"])
            
            # Submit to Celery task queue
            task = process_single_tool_url.delay(
                url=tool["url"],
                title=tool["title"],
                source="searxng_discovery",
            )
            
            logger.info("Task submitted", task_id=task.id, title=tool["title"])
            processed += 1
            
        except Exception as e:
            logger.error("Failed to process tool", error=str(e), url=tool["url"])
    
    return processed


async def main():
    """Main discovery and processing loop"""
    logger.info("Starting AI tool discovery via SearXNG")
    
    # Step 1: Discover tools
    tools = await discover_ai_tools()
    logger.info("Discovery complete", total_found=len(tools))
    
    if not tools:
        logger.warning("No tools discovered!")
        return
    
    # Print discovered tools
    print("\n" + "="*60)
    print("DISCOVERED AI TOOLS (sorted by likelihood score)")
    print("="*60)
    
    for i, tool in enumerate(tools[:20], 1):
        print(f"\n{i}. {tool['title'][:60]}")
        print(f"   URL: {tool['url'][:70]}")
        print(f"   Score: {tool['tool_score']:.2f}")
        print(f"   {tool['description'][:100]}...")
    
    print("\n" + "="*60)
    print(f"Total discovered: {len(tools)} potential AI tools")
    print("="*60)
    
    # Step 2: Process top tools
    if len(sys.argv) > 1 and sys.argv[1] == "--process":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(f"\nProcessing top {limit} tools...")
        processed = await process_discovered_tools(tools, limit=limit)
        print(f"Submitted {processed} tools to processing queue")
    else:
        print("\nRun with --process [N] to submit top N tools to the pipeline")


if __name__ == "__main__":
    asyncio.run(main())

