"""
Citation Manager Agent

Responsible for:
- Validating source URLs
- Extracting and formatting citations
- Ensuring proper attribution
- Detecting potential plagiarism
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.core.config import settings
from app.models.content import Citation


class CitationAgent(BaseAgent):
    """
    Citation Manager Agent
    
    Validates sources, formats citations, and ensures proper attribution
    for all content.
    """
    
    name = "citation"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.http_client = httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": settings.USER_AGENT},
        )
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Process and validate citations"""
        try:
            citations = []
            
            # Collect all source URLs from context
            source_urls = self._collect_source_urls(context)
            
            # Validate and enrich each source
            for url in source_urls:
                citation = await self._validate_and_enrich_url(url)
                if citation:
                    citations.append(citation)
                    context.add_citation(
                        url=citation["url"],
                        title=citation["title"],
                        source=citation["source_name"],
                        snippet=citation.get("snippet"),
                    )
            
            # Store citations in context
            context.metadata["validated_citations"] = citations
            
            # Update processed content with citations
            if context.processed_content:
                context.processed_content["citations"] = citations
                context.processed_content["source_count"] = len(citations)
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output={
                    "total_sources": len(source_urls),
                    "validated_citations": len(citations),
                    "citations": citations,
                },
            )
            
        except Exception as e:
            self.logger.error("Citation processing failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    def _collect_source_urls(self, context: AgentContext) -> List[str]:
        """Collect all source URLs from context"""
        urls = set()
        
        # Primary source URL
        if context.source_url:
            urls.add(context.source_url)
        
        # URLs from metadata
        if context.metadata.get("search_results"):
            for result in context.metadata["search_results"]:
                if result.get("url"):
                    urls.add(result["url"])
        
        # URLs from scraped data
        if context.metadata.get("scraped_data", {}).get("links"):
            for link in context.metadata["scraped_data"]["links"][:10]:
                if link.get("href"):
                    urls.add(link["href"])
        
        # URLs from processed content
        if context.processed_content and context.processed_content.get("source_urls"):
            for url in context.processed_content["source_urls"]:
                urls.add(url)
        
        return list(urls)[:20]  # Limit to 20 sources
    
    async def _validate_and_enrich_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Validate a URL and extract citation metadata"""
        try:
            # Skip invalid URLs
            if not url.startswith(("http://", "https://")):
                return None
            
            # HEAD request to check if URL is accessible
            response = await self.http_client.head(url)
            
            if response.status_code >= 400:
                self.logger.warning("URL not accessible", url=url, status=response.status_code)
                return None
            
            # GET request to extract metadata
            response = await self.http_client.get(url)
            
            if response.status_code >= 400:
                return None
            
            # Extract metadata from HTML
            metadata = self._extract_metadata(response.text, url)
            
            return {
                "url": url,
                "title": metadata.get("title", "Untitled"),
                "source_name": self._extract_domain(url),
                "snippet": metadata.get("description", "")[:300],
                "author": metadata.get("author"),
                "published_date": metadata.get("published_date"),
                "accessed_at": datetime.utcnow().isoformat(),
                "status": "verified",
            }
            
        except httpx.TimeoutException:
            self.logger.warning("URL timeout", url=url)
            return None
        except Exception as e:
            self.logger.warning("URL validation failed", url=url, error=str(e))
            return None
    
    def _extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML content"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "lxml")
        
        metadata = {}
        
        # Title
        if soup.title:
            metadata["title"] = soup.title.string
        else:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                metadata["title"] = og_title.get("content")
        
        # Description
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            metadata["description"] = meta_desc.get("content", "")
        else:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                metadata["description"] = og_desc.get("content", "")
        
        # Author
        author_meta = soup.find("meta", {"name": "author"})
        if author_meta:
            metadata["author"] = author_meta.get("content")
        
        # Published date
        date_meta = soup.find("meta", {"property": "article:published_time"})
        if date_meta:
            metadata["published_date"] = date_meta.get("content")
        
        return metadata
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    
    async def format_citations_markdown(self, citations: List[Dict[str, Any]]) -> str:
        """Format citations as Markdown for inclusion in content"""
        if not citations:
            return ""
        
        lines = ["## Sources", ""]
        
        for i, citation in enumerate(citations, 1):
            title = citation.get("title", "Untitled")
            url = citation.get("url", "")
            source = citation.get("source_name", "Unknown")
            accessed = citation.get("accessed_at", "")
            
            lines.append(f"{i}. [{title}]({url}) - *{source}*")
        
        return "\n".join(lines)
    
    async def check_plagiarism(self, content: str, sources: List[str]) -> Dict[str, Any]:
        """
        Basic plagiarism check by comparing content against sources.
        Returns similarity scores.
        """
        # This is a placeholder - in production, you'd use a proper
        # plagiarism detection service or implement content fingerprinting
        return {
            "is_original": True,
            "similarity_score": 0.0,
            "matched_sources": [],
            "note": "Plagiarism check is a placeholder implementation",
        }
    
    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()

