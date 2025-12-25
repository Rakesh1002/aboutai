"""
Rewriter Agent

Final polishing of content:
- Grammar and style improvements
- Consistency checks
- Tone alignment with aboutai voice
- Quality assurance
"""
from typing import Dict, Any
import json
import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.core.config import settings


REWRITE_PROMPT = """You are the final editor for aboutai.com, ensuring all content meets our high editorial standards.

Review and polish the following {content_type} content:

## Current Content:
{content}

## Editorial Guidelines:
1. **Voice**: Professional, authoritative, but accessible
2. **Tone**: Objective and analytical - cut through hype
3. **Style**: Clear, concise sentences. Active voice preferred.
4. **Accuracy**: Don't add claims not supported by the source material
5. **aboutai Brand**: 
   - We are the "trust engine" of the AI economy
   - We verify, not just aggregate
   - We help readers make informed decisions

## Tasks:
1. Fix any grammatical errors
2. Improve sentence flow and readability
3. Ensure consistent tone throughout
4. Remove any marketing fluff or unsupported claims
5. Strengthen the opening paragraph
6. Ensure proper technical accuracy
7. Add transition sentences where needed

## Rules:
- Do NOT change facts or add new information
- Do NOT change the structure (headings, sections)
- Do NOT modify the frontmatter
- Keep the same approximate length
- Preserve all links and citations

## Output:
Return the polished content in the same format (MDX with frontmatter).
Only return the content, no explanations.
"""

QUALITY_CHECK_PROMPT = """Perform a quality check on this content:

{content}

Rate the following on a scale of 1-10:
1. Grammar & spelling
2. Clarity & readability
3. Factual accuracy (based on citations)
4. Objectivity (free from bias/hype)
5. Completeness
6. SEO optimization

Output as JSON:
{{
    "scores": {{
        "grammar": 1-10,
        "clarity": 1-10,
        "accuracy": 1-10,
        "objectivity": 1-10,
        "completeness": 1-10,
        "seo": 1-10
    }},
    "overall_score": 1-10,
    "issues": ["list of specific issues found"],
    "suggestions": ["list of improvement suggestions"],
    "ready_for_publication": true/false
}}
"""


class RewriterAgent(BaseAgent):
    """
    Rewriter Agent
    
    Final pass on content to ensure quality, consistency,
    and alignment with aboutai's editorial voice.
    """
    
    name = "rewriter"
    version = "1.0.0"
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Polish and finalize content"""
        try:
            mdx_content = context.metadata.get("mdx_content", "")
            
            if not mdx_content:
                return AgentResult(
                    success=False,
                    agent_name=self.name,
                    error="No MDX content to rewrite",
                )
            
            # First pass: Quality check
            quality_check = await self._quality_check(mdx_content)
            
            # If quality is low, perform rewrite
            if quality_check.get("overall_score", 0) < 7:
                self.logger.info("Content needs rewriting", score=quality_check.get("overall_score"))
                mdx_content = await self._rewrite_content(context, mdx_content)
                
                # Re-check quality
                quality_check = await self._quality_check(mdx_content)
            
            # Update context with final content
            context.metadata["final_mdx"] = mdx_content
            context.metadata["quality_check"] = quality_check
            context.processed_content["mdx"] = mdx_content
            context.processed_content["quality_score"] = quality_check.get("overall_score", 0)
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output={
                    "quality_score": quality_check.get("overall_score", 0),
                    "ready_for_publication": quality_check.get("ready_for_publication", False),
                    "issues_found": len(quality_check.get("issues", [])),
                },
            )
            
        except Exception as e:
            self.logger.error("Rewriting failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    async def _rewrite_content(self, context: AgentContext, content: str) -> str:
        """Rewrite content to improve quality"""
        client, model = self.get_llm_client()
        
        prompt = REWRITE_PROMPT.format(
            content_type=context.content_type,
            content=content,
        )
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert editor. Return only the edited content."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()
    
    async def _quality_check(self, content: str) -> Dict[str, Any]:
        """Perform quality check on content"""
        client, model = self.get_llm_client()
        
        prompt = QUALITY_CHECK_PROMPT.format(content=content[:4000])
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a content quality assessor. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _check_consistency(self, content: str) -> Dict[str, Any]:
        """Check for internal consistency"""
        # Check for common issues
        issues = []
        
        # Check for placeholder text
        if "[placeholder]" in content.lower() or "todo" in content.lower():
            issues.append("Contains placeholder text")
        
        # Check for broken links syntax
        import re
        broken_links = re.findall(r'\[.*?\]\(\s*\)', content)
        if broken_links:
            issues.append(f"Contains {len(broken_links)} empty links")
        
        # Check for missing sections
        if "## Features" not in content and "tool" in content.lower():
            issues.append("Missing Features section for tool listing")
        
        return {
            "issues": issues,
            "is_consistent": len(issues) == 0,
        }
    
    def extract_frontmatter(self, mdx_content: str) -> tuple[Dict[str, Any], str]:
        """Extract frontmatter and body from MDX content"""
        import yaml
        
        if not mdx_content.startswith("---"):
            return {}, mdx_content
        
        # Find the closing ---
        end_index = mdx_content.find("---", 3)
        if end_index == -1:
            return {}, mdx_content
        
        frontmatter_str = mdx_content[3:end_index].strip()
        body = mdx_content[end_index + 3:].strip()
        
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            frontmatter = {}
        
        return frontmatter, body

