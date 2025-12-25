"""
Formatter Agent

Formats content into the final MDX structure for the frontend.
Handles:
- MDX frontmatter generation
- Content structure formatting
- Image/asset references
- Link formatting
"""
from typing import Dict, Any, Optional
from datetime import datetime
import re
import structlog
from slugify import slugify

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.core.config import settings


class FormatterAgent(BaseAgent):
    """
    Formatter Agent
    
    Converts processed content into MDX format ready for the frontend.
    """
    
    name = "formatter"
    version = "1.0.0"
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Format content into MDX"""
        try:
            if context.content_type == "tool":
                mdx_content = self._format_tool_mdx(context)
            else:
                mdx_content = self._format_news_mdx(context)
            
            # Store formatted content
            context.metadata["mdx_content"] = mdx_content
            context.processed_content["mdx"] = mdx_content
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output={
                    "mdx_length": len(mdx_content),
                    "content_type": context.content_type,
                },
            )
            
        except Exception as e:
            self.logger.error("Formatting failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    def _format_tool_mdx(self, context: AgentContext) -> str:
        """Format a tool listing as MDX"""
        pc = context.processed_content or {}
        enrichments = context.metadata.get("enrichments", {})
        citations = context.metadata.get("validated_citations", [])
        
        # Generate frontmatter
        frontmatter = {
            "title": pc.get("title", "Untitled Tool"),
            "description": pc.get("description", ""),
            "url": context.source_url or pc.get("url", ""),
            "trust_score": enrichments.get("trust_score", {}).get("total", 0),
            "is_wrapper": enrichments.get("wrapper_analysis", {}).get("wrapper_status") == "wrapper",
            "wrapper_status": enrichments.get("wrapper_analysis", {}).get("wrapper_status", "unknown"),
            "type": self._get_type_label(enrichments.get("wrapper_analysis", {}).get("wrapper_status")),
            "vertical": enrichments.get("classification", {}).get("primary_vertical", "general"),
            "categories": pc.get("categories", enrichments.get("classification", {}).get("categories", [])),
            "tags": pc.get("suggested_tags", []),
            "pricing": pc.get("pricing_info", "Unknown"),
            "featured": False,
            "verified": False,
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
        }
        
        # Build MDX content
        mdx_parts = [
            self._format_frontmatter(frontmatter),
            "",
            pc.get("long_description", "No description available."),
            "",
        ]
        
        # Features section
        features = pc.get("features", [])
        if features:
            mdx_parts.extend([
                "## Features",
                "",
            ])
            for feature in features:
                mdx_parts.append(f"- {feature}")
            mdx_parts.append("")
        
        # Use cases section
        use_cases = pc.get("use_cases", [])
        if use_cases:
            mdx_parts.extend([
                "## Use Cases",
                "",
            ])
            for use_case in use_cases:
                mdx_parts.append(f"- {use_case}")
            mdx_parts.append("")
        
        # Trust Score Breakdown
        trust_score = enrichments.get("trust_score", {})
        if trust_score.get("breakdown"):
            breakdown = trust_score["breakdown"]
            mdx_parts.extend([
                "## Trust Score Breakdown",
                "",
                f"Our autonomous testing system analyzed this tool and assigned a Trust Score of **{trust_score.get('total', 0)}**.",
                "",
                f"- **Proprietary Technology**: {breakdown.get('proprietary', 0)}/100",
                f"- **Reliability**: {breakdown.get('reliability', 0)}/100",
                f"- **Transparency**: {breakdown.get('transparency', 0)}/100",
                f"- **Liveness**: {breakdown.get('liveness', 0)}/100",
                "",
            ])
        
        # Wrapper Analysis
        wrapper = enrichments.get("wrapper_analysis", {})
        if wrapper:
            mdx_parts.extend([
                "## Wrapper Analysis",
                "",
                f"**Status**: {self._get_type_label(wrapper.get('wrapper_status', 'unknown'))}",
                "",
                wrapper.get("reasoning", ""),
                "",
            ])
        
        # Sources
        if citations:
            mdx_parts.extend([
                "## Sources",
                "",
            ])
            for i, citation in enumerate(citations[:5], 1):
                mdx_parts.append(f"{i}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})")
            mdx_parts.append("")
        
        return "\n".join(mdx_parts)
    
    def _format_news_mdx(self, context: AgentContext) -> str:
        """Format a news article as MDX"""
        pc = context.processed_content or {}
        enrichments = context.metadata.get("enrichments", {})
        citations = context.metadata.get("validated_citations", [])
        
        # Generate frontmatter
        frontmatter = {
            "title": pc.get("title", "Untitled Article"),
            "description": pc.get("description", ""),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "hype_score": pc.get("hype_score", 50),
            "vertical": enrichments.get("classification", {}).get("primary_vertical", "general"),
            "tags": pc.get("suggested_tags", []),
            "author": "aboutai Research Team",
            "source_url": context.source_url or "",
        }
        
        # Build MDX content
        mdx_parts = [
            self._format_frontmatter(frontmatter),
            "",
            pc.get("content", "No content available."),
            "",
        ]
        
        # Hype Meter
        hype_score = pc.get("hype_score", 50)
        hype_label = self._get_hype_label(hype_score)
        mdx_parts.extend([
            "---",
            "",
            f"**Hype Meter**: {hype_label} ({hype_score}/100)",
            "",
        ])
        
        # Sources
        if citations:
            mdx_parts.extend([
                "## Sources",
                "",
            ])
            for i, citation in enumerate(citations[:5], 1):
                mdx_parts.append(f"{i}. [{citation.get('title', 'Source')}]({citation.get('url', '#')})")
            mdx_parts.append("")
        
        return "\n".join(mdx_parts)
    
    def _format_frontmatter(self, data: Dict[str, Any]) -> str:
        """Format frontmatter as YAML"""
        import yaml
        
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        return f"---\n{yaml_content}---"
    
    def _get_type_label(self, wrapper_status: str) -> str:
        """Get human-readable type label"""
        labels = {
            "native": "⚡ Native AI",
            "fine_tuned": "🎯 Fine-Tuned",
            "rag": "📚 RAG-Enhanced",
            "wrapper": "📦 Wrapper",
            "unknown": "❓ Unknown",
        }
        return labels.get(wrapper_status, "❓ Unknown")
    
    def _get_hype_label(self, score: int) -> str:
        """Get hype level label"""
        if score >= 80:
            return "🔥 Very High"
        elif score >= 60:
            return "📈 High"
        elif score >= 40:
            return "📊 Moderate"
        elif score >= 20:
            return "📉 Low"
        else:
            return "💤 Minimal"
    
    def generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        return slugify(title, max_length=60)

