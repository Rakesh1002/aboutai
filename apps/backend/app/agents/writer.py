"""
Writer Agent

Generates initial content drafts from scraped/researched data.
Uses LLMs to create well-structured, informative content.
"""
from typing import Dict, Any, Optional
import json
import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.core.config import settings


TOOL_WRITING_PROMPT = """You are an expert AI technology writer for aboutai.com, a trusted platform for AI tool reviews and news.

Your task is to write a comprehensive tool listing based on the provided research data.

## Research Data:
{research_data}

## Source URL:
{source_url}

## Instructions:
1. Write a clear, factual description of the tool (2-3 sentences)
2. Create a detailed long description (2-3 paragraphs) covering:
   - What the tool does and its primary use cases
   - Key differentiators and unique features
   - Who the tool is designed for (target audience)
3. List 5-8 key features as bullet points
4. List 3-5 use cases
5. Suggest appropriate categorization

## Writing Guidelines:
- Be factual and objective - avoid marketing language
- Focus on verifiable capabilities
- Highlight both strengths and limitations if known
- Use clear, professional language
- DO NOT invent features not mentioned in the research

## Output Format (JSON):
{{
    "title": "Tool Name",
    "slug": "tool-name",
    "description": "Brief 2-3 sentence description",
    "long_description": "Detailed 2-3 paragraph description",
    "features": ["Feature 1", "Feature 2", ...],
    "use_cases": ["Use case 1", "Use case 2", ...],
    "suggested_vertical": "one of: agtech, legal, devtools, marketing, healthcare, finance, education, general",
    "suggested_categories": ["category1", "category2"],
    "suggested_tags": ["tag1", "tag2", ...],
    "pricing_info": "Any pricing information found"
}}
"""

NEWS_WRITING_PROMPT = """You are an expert AI journalist for aboutai.com, providing thoughtful, analytical coverage of AI developments.

Your task is to write a news article based on the provided research data.

## Research Data:
{research_data}

## Original Sources:
{sources}

## Instructions:
1. Write a compelling headline that accurately represents the story
2. Create a concise description/lede (1-2 sentences)
3. Write the full article (3-5 paragraphs) that:
   - Opens with the most important information
   - Provides context and background
   - Includes relevant quotes or data points
   - Analyzes implications for the AI industry
   - Maintains objectivity while being engaging
4. Assess the "hype level" of this news (0-100):
   - 0-20: Routine/incremental update
   - 21-40: Notable development
   - 41-60: Significant news
   - 61-80: Major development
   - 81-100: Transformative/paradigm-shifting

## Writing Guidelines:
- Be factual and cite sources
- Cut through marketing hype - focus on substance
- Provide context for technical readers
- Avoid sensationalism
- If the news is about a "wrapper" or thin AI application, note this

## Output Format (JSON):
{{
    "title": "Article Headline",
    "slug": "article-slug",
    "description": "Brief 1-2 sentence description/lede",
    "content": "Full article content in Markdown format",
    "suggested_vertical": "one of: agtech, legal, devtools, marketing, healthcare, finance, education, general",
    "suggested_tags": ["tag1", "tag2", ...],
    "hype_score": 50,
    "key_entities": ["Company/Person/Tool mentioned"],
    "source_urls": ["url1", "url2"]
}}
"""


class WriterAgent(BaseAgent):
    """
    Writer Agent
    
    Takes research data and generates well-structured content drafts
    using LLM-powered writing.
    """
    
    name = "writer"
    version = "1.0.0"
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Generate content from research data"""
        try:
            if context.content_type == "tool":
                output = await self._write_tool_listing(context)
            else:
                output = await self._write_news_article(context)
            
            # Store generated content in context
            context.processed_content = output
            context.metadata["writer_output"] = output
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output=output,
            )
            
        except Exception as e:
            self.logger.error("Writing failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    async def _write_tool_listing(self, context: AgentContext) -> Dict[str, Any]:
        """Generate a tool listing"""
        client, model = self.get_llm_client()
        
        # Prepare research data
        research_data = self._prepare_research_data(context)
        
        prompt = TOOL_WRITING_PROMPT.format(
            research_data=research_data,
            source_url=context.source_url or "Not specified",
        )
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert AI technology writer. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _write_news_article(self, context: AgentContext) -> Dict[str, Any]:
        """Generate a news article"""
        client, model = self.get_llm_client()
        
        # Prepare research data
        research_data = self._prepare_research_data(context)
        sources = self._format_sources(context)
        
        prompt = NEWS_WRITING_PROMPT.format(
            research_data=research_data,
            sources=sources,
        )
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert AI journalist. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _prepare_research_data(self, context: AgentContext) -> str:
        """Prepare research data for the prompt"""
        parts = []
        
        if context.raw_content:
            parts.append(f"## Raw Content:\n{context.raw_content[:5000]}")
        
        if context.metadata.get("scraped_data"):
            data = context.metadata["scraped_data"]
            parts.append(f"## Scraped Data:\nTitle: {data.get('title', 'N/A')}\nDescription: {data.get('description', 'N/A')}")
        
        if context.metadata.get("search_results"):
            results = context.metadata["search_results"][:5]
            parts.append("## Related Search Results:")
            for r in results:
                parts.append(f"- {r.get('title', 'N/A')}: {r.get('description', 'N/A')[:200]}")
        
        return "\n\n".join(parts)
    
    def _format_sources(self, context: AgentContext) -> str:
        """Format sources for citation"""
        sources = []
        
        if context.source_url:
            sources.append(context.source_url)
        
        if context.metadata.get("search_results"):
            for r in context.metadata["search_results"][:5]:
                sources.append(f"- {r.get('url', 'N/A')}: {r.get('title', 'N/A')}")
        
        return "\n".join(sources) if sources else "No external sources"

