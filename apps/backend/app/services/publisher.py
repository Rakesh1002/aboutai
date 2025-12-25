"""
MDX Content Publisher for aboutai.
Generates and writes MDX files to the frontend content directory.
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import yaml
import structlog
import asyncio

from app.core.config import settings
from app.models import ToolData, NewsData, ContentStatus, WrapperStatus, Vertical

logger = structlog.get_logger()


class MDXPublisher:
    """
    Publishes content as MDX files to the frontend.
    Handles both tool listings and news articles.
    """
    
    def __init__(self):
        self.content_dir = Path(settings.FRONTEND_CONTENT_DIR)
        self.tools_dir = self.content_dir / "tools"
        self.news_dir = self.content_dir / "news"
        
        # Ensure directories exist
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.news_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "MDXPublisher initialized",
            content_dir=str(self.content_dir),
        )
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and special chars with hyphens
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        # Remove leading/trailing hyphens
        text = text.strip("-")
        return text[:100]  # Limit length
    
    def _format_yaml_value(self, value: Any) -> str:
        """Format a value for YAML frontmatter"""
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(value, list):
            return "\n" + "\n".join(f"  - {item}" for item in value)
        elif isinstance(value, dict):
            return "\n" + "\n".join(f"  {k}: {v}" for k, v in value.items())
        elif value is None:
            return ""
        else:
            return str(value)
    
    def publish_tool(self, tool: ToolData) -> str:
        """
        Publish a tool as an MDX file.
        Returns the file path.
        """
        # Generate slug if not provided
        slug = tool.slug or self._slugify(tool.name)
        
        # Build frontmatter
        frontmatter = {
            "name": tool.name,
            "slug": slug,
            "description": tool.description[:300] if tool.description else "",
            "url": str(tool.url),
            "logoUrl": tool.logo_url or f"/images/tools/{slug}.png",
            "vertical": tool.vertical.value if isinstance(tool.vertical, Vertical) else tool.vertical,
            "categories": tool.categories or ["general"],
            "tags": tool.tags or [],
            "trustScore": tool.trust_score,
            "wrapperStatus": tool.wrapper_status.value if isinstance(tool.wrapper_status, WrapperStatus) else tool.wrapper_status,
            "isVerified": tool.is_verified,
            "pricing": {
                "type": tool.pricing.type.value if hasattr(tool.pricing.type, 'value') else tool.pricing.type,
                "startingPrice": tool.pricing.starting_price,
                "currency": tool.pricing.currency,
                "billingPeriod": tool.pricing.billing_period,
            },
            "lastAuditedAt": tool.last_audited_at.isoformat() if tool.last_audited_at else datetime.utcnow().isoformat(),
            "createdAt": tool.created_at.isoformat() if tool.created_at else datetime.utcnow().isoformat(),
        }
        
        # Generate MDX content
        mdx_content = self._generate_tool_mdx(tool, frontmatter)
        
        # Write to file
        file_path = self.tools_dir / f"{slug}.mdx"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(mdx_content)
        
        logger.info("Published tool MDX", name=tool.name, path=str(file_path))
        return str(file_path)
    
    def _generate_tool_mdx(self, tool: ToolData, frontmatter: dict) -> str:
        """Generate complete MDX content for a tool"""
        # YAML frontmatter
        yaml_content = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        
        # Determine wrapper description
        wrapper_desc = {
            WrapperStatus.NATIVE: "Native AI application with proprietary technology",
            WrapperStatus.FINE_TUNED: "Uses fine-tuned models for domain expertise",
            WrapperStatus.RAG: "RAG-enhanced with proprietary knowledge base",
            WrapperStatus.WRAPPER: "UI layer over foundation model APIs",
            WrapperStatus.UNKNOWN: "Technology stack not yet verified",
        }
        
        wrapper_status = tool.wrapper_status if isinstance(tool.wrapper_status, WrapperStatus) else WrapperStatus(tool.wrapper_status)
        wrapper_text = wrapper_desc.get(wrapper_status, "Unknown")
        
        # Build MDX body
        body = f"""# {tool.name}

<TrustScoreBadge score={{{tool.trust_score}}} />

{tool.description}

## Overview

{tool.content if tool.content else f"{tool.name} is an AI tool in the {tool.vertical} space."}

## Why Trust Score: {tool.trust_score}

<Callout type="{'success' if tool.trust_score >= 70 else 'warning' if tool.trust_score >= 40 else 'error'}">
**{'Verified ' if tool.is_verified else ''}{wrapper_status.value.replace('_', ' ').title()}**: {wrapper_text}
</Callout>

| Factor | Score | Notes |
|--------|-------|-------|
| Proprietary Tech | {tool.proprietary_tech_score} | {'Custom model/fine-tuning detected' if tool.proprietary_tech_score >= 70 else 'Limited proprietary indicators'} |
| Reliability | {tool.reliability_score} | Based on automated testing |
| Transparency | {tool.transparency_score} | {'Clear documentation' if tool.transparency_score >= 70 else 'Limited transparency'} |
| Liveness | {tool.liveness_score} | {'Actively maintained' if tool.liveness_score >= 70 else 'Activity level unclear'} |

"""

        # Add detected technologies if available
        if tool.detected_technologies:
            body += f"""
## Detected Technologies

{', '.join(tool.detected_technologies[:10])}

"""

        # Add API dependencies warning if wrapper
        if tool.api_dependencies:
            body += f"""
<Callout type="warning">
**API Dependencies Detected**: This tool relies on {', '.join(tool.api_dependencies)}.
</Callout>

"""

        # Add pricing section
        if tool.pricing:
            body += f"""
## Pricing

| Tier | Price | Features |
|------|-------|----------|
| {tool.pricing.type.value.title() if hasattr(tool.pricing.type, 'value') else tool.pricing.type.title()} | {'$' + str(tool.pricing.starting_price) + '/' + (tool.pricing.billing_period or 'mo') if tool.pricing.starting_price else 'Free'} | Core features |

"""

        # Add audit timestamp
        body += f"""
---

*Last audited: {tool.last_audited_at.strftime('%B %d, %Y') if tool.last_audited_at else datetime.utcnow().strftime('%B %d, %Y')}*
"""

        return f"---\n{yaml_content}---\n\n{body}"
    
    def publish_news(self, news: NewsData) -> str:
        """
        Publish a news article as an MDX file.
        Returns the file path.
        """
        # Generate slug if not provided
        slug = news.slug or self._slugify(news.title)
        
        # Build frontmatter
        frontmatter = {
            "title": news.title,
            "slug": slug,
            "excerpt": news.excerpt[:300] if news.excerpt else "",
            "author": news.author or "aboutai Team",
            "publishedAt": (news.published_at or datetime.utcnow()).isoformat(),
            "vertical": news.vertical.value if isinstance(news.vertical, Vertical) else news.vertical,
            "tags": news.tags or [],
            "hypeScore": news.hype_score,
            "coverImage": news.cover_image or f"/images/news/{slug}.jpg",
            "status": "published",
        }
        
        # Generate MDX content
        mdx_content = self._generate_news_mdx(news, frontmatter)
        
        # Write to file
        file_path = self.news_dir / f"{slug}.mdx"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(mdx_content)
        
        logger.info("Published news MDX", title=news.title, path=str(file_path))
        return str(file_path)
    
    def _generate_news_mdx(self, news: NewsData, frontmatter: dict) -> str:
        """Generate complete MDX content for a news article"""
        # YAML frontmatter
        yaml_content = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        
        # Determine hype level description
        if news.hype_score <= 20:
            hype_text = "Highly factual, well-sourced reporting"
            callout_type = "success"
        elif news.hype_score <= 50:
            hype_text = "Balanced coverage with some promotional language"
            callout_type = "info"
        elif news.hype_score <= 75:
            hype_text = "Contains notable hype indicators"
            callout_type = "warning"
        else:
            hype_text = "High sensationalism detected - read critically"
            callout_type = "error"
        
        # Build MDX body
        body = f"""# {news.title}

<Callout type="{callout_type}">
**Hype Score: {news.hype_score}/100** — {hype_text}
</Callout>

{news.content if news.content else news.excerpt}

"""

        # Add hype analysis details if available
        if news.sensationalism_signals:
            body += f"""
## Hype Analysis

**Sensationalism indicators detected**: {', '.join(news.sensationalism_signals[:5])}

"""
        
        if news.factual_signals:
            body += f"""**Factual indicators**: {', '.join(news.factual_signals[:5])}

"""

        # Add citations if available
        if news.citations:
            body += """
## Sources

"""
            for i, citation in enumerate(news.citations[:10], 1):
                body += f"- [{citation}]({citation})\n"

        # Add footer
        body += f"""
---

*Published: {(news.published_at or datetime.utcnow()).strftime('%B %d, %Y')} by {news.author}*
"""

        if news.source_url:
            body += f"\n*Original source: [{news.source_url}]({news.source_url})*\n"

        return f"---\n{yaml_content}---\n\n{body}"
    
    def list_published_tools(self) -> List[str]:
        """List all published tool slugs"""
        return [f.stem for f in self.tools_dir.glob("*.mdx")]
    
    def list_published_news(self) -> List[str]:
        """List all published news slugs"""
        return [f.stem for f in self.news_dir.glob("*.mdx")]
    
    def is_tool_published(self, slug: str) -> bool:
        """Check if a tool is already published"""
        return (self.tools_dir / f"{slug}.mdx").exists()
    
    def is_news_published(self, slug: str) -> bool:
        """Check if a news article is already published"""
        return (self.news_dir / f"{slug}.mdx").exists()
    
    def delete_tool(self, slug: str) -> bool:
        """Delete a published tool"""
        file_path = self.tools_dir / f"{slug}.mdx"
        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted tool MDX", slug=slug)
            return True
        return False
    
    def delete_news(self, slug: str) -> bool:
        """Delete a published news article"""
        file_path = self.news_dir / f"{slug}.mdx"
        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted news MDX", slug=slug)
            return True
        return False


class ContentDraftStore:
    """
    Manages content drafts before publication.
    Uses file-based storage (could be replaced with database).
    """
    
    def __init__(self):
        self.drafts_dir = Path(settings.DRAFTS_DIR)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        
        self.tools_drafts_dir = self.drafts_dir / "tools"
        self.news_drafts_dir = self.drafts_dir / "news"
        
        self.tools_drafts_dir.mkdir(exist_ok=True)
        self.news_drafts_dir.mkdir(exist_ok=True)
    
    def save_tool_draft(self, draft_id: str, tool: ToolData, quality_score: float = 0.0) -> str:
        """Save a tool draft"""
        draft = {
            "id": draft_id,
            "type": "tool",
            "status": ContentStatus.PENDING_REVIEW.value,
            "quality_score": quality_score,
            "data": tool.model_dump(mode="json"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        file_path = self.tools_drafts_dir / f"{draft_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=2, default=str)
        
        logger.info("Saved tool draft", draft_id=draft_id, name=tool.name)
        return str(file_path)
    
    def save_news_draft(self, draft_id: str, news: NewsData, quality_score: float = 0.0) -> str:
        """Save a news draft"""
        draft = {
            "id": draft_id,
            "type": "news",
            "status": ContentStatus.PENDING_REVIEW.value,
            "quality_score": quality_score,
            "data": news.model_dump(mode="json"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        file_path = self.news_drafts_dir / f"{draft_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=2, default=str)
        
        logger.info("Saved news draft", draft_id=draft_id, title=news.title)
        return str(file_path)
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a draft by ID"""
        # Check tools
        tool_path = self.tools_drafts_dir / f"{draft_id}.json"
        if tool_path.exists():
            with open(tool_path, "r") as f:
                return json.load(f)
        
        # Check news
        news_path = self.news_drafts_dir / f"{draft_id}.json"
        if news_path.exists():
            with open(news_path, "r") as f:
                return json.load(f)
        
        return None
    
    def list_drafts(
        self,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List all drafts"""
        drafts = []
        
        # Get tool drafts
        if content_type is None or content_type == "tool":
            for file_path in self.tools_drafts_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    draft = json.load(f)
                    if status is None or draft.get("status") == status:
                        drafts.append(draft)
        
        # Get news drafts
        if content_type is None or content_type == "news":
            for file_path in self.news_drafts_dir.glob("*.json"):
                with open(file_path, "r") as f:
                    draft = json.load(f)
                    if status is None or draft.get("status") == status:
                        drafts.append(draft)
        
        # Sort by created_at descending
        drafts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return drafts[:limit]
    
    def update_draft_status(
        self,
        draft_id: str,
        status: ContentStatus,
        notes: Optional[str] = None,
    ) -> bool:
        """Update draft status"""
        draft = self.get_draft(draft_id)
        if not draft:
            return False
        
        draft["status"] = status.value
        draft["updated_at"] = datetime.utcnow().isoformat()
        if notes:
            draft["reviewer_notes"] = notes
        
        # Determine file path
        if draft["type"] == "tool":
            file_path = self.tools_drafts_dir / f"{draft_id}.json"
        else:
            file_path = self.news_drafts_dir / f"{draft_id}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=2, default=str)
        
        logger.info("Updated draft status", draft_id=draft_id, status=status.value)
        return True
    
    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft"""
        # Check tools
        tool_path = self.tools_drafts_dir / f"{draft_id}.json"
        if tool_path.exists():
            tool_path.unlink()
            logger.info("Deleted tool draft", draft_id=draft_id)
            return True
        
        # Check news
        news_path = self.news_drafts_dir / f"{draft_id}.json"
        if news_path.exists():
            news_path.unlink()
            logger.info("Deleted news draft", draft_id=draft_id)
            return True
        
        return False
