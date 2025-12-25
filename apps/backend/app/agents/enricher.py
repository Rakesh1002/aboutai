"""
Content Enricher Agent

Enriches content with:
- Trust score analysis (for tools)
- Hype score validation (for news)
- Additional metadata
- Related content suggestions
- Vertical/category classification
"""
from typing import Dict, Any, List
import json
import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.core.config import settings


WRAPPER_ANALYSIS_PROMPT = """You are an expert AI systems analyst specializing in identifying "wrapper" applications.

A "wrapper" is an AI tool that is primarily a thin UI layer over foundation model APIs (like OpenAI, Anthropic) with minimal proprietary technology. 

Analyze this tool and determine its "wrapper status":

## Tool Information:
{tool_info}

## Analysis Criteria:
1. **Native AI** (0-20% wrapper likelihood): Custom-trained models, significant R&D, proprietary algorithms
2. **Fine-Tuned** (21-40%): Fine-tuned foundation models with domain-specific training
3. **RAG-Enhanced** (41-60%): Retrieval-augmented generation with proprietary knowledge bases
4. **Light Wrapper** (61-80%): Adds meaningful UX/workflow but relies heavily on foundation APIs
5. **Pure Wrapper** (81-100%): Essentially a UI over GPT/Claude with minimal added value

## Signals to Look For:
- Does it mention custom models or training?
- Are there unique features not available in ChatGPT/Claude directly?
- Does it have domain-specific knowledge or data?
- Is the pricing sustainable (or just API arbitrage)?
- Does it have enterprise/compliance features?

## Output Format (JSON):
{{
    "wrapper_status": "native|fine_tuned|rag|wrapper",
    "wrapper_likelihood": 0-100,
    "confidence": 0-100,
    "reasoning": "Brief explanation",
    "signals": {{
        "has_custom_model": true/false,
        "has_proprietary_data": true/false,
        "has_unique_features": true/false,
        "has_enterprise_features": true/false,
        "sustainable_pricing": true/false
    }},
    "red_flags": ["Any concerning patterns"],
    "green_flags": ["Positive indicators"]
}}
"""

VERTICAL_CLASSIFICATION_PROMPT = """Classify this AI tool/news into the most appropriate vertical and categories.

## Content:
{content}

## Available Verticals:
- agtech: Agriculture, farming, food production
- legal: Law, contracts, compliance
- devtools: Developer tools, coding assistants, DevOps
- marketing: Marketing, content creation, advertising
- healthcare: Medical, health, wellness
- finance: Banking, investing, fintech
- education: Learning, tutoring, academic
- general: General purpose, consumer

## Output Format (JSON):
{{
    "primary_vertical": "vertical_name",
    "secondary_verticals": ["other_relevant_verticals"],
    "categories": ["specific_categories"],
    "confidence": 0-100,
    "reasoning": "Brief explanation"
}}
"""


class EnricherAgent(BaseAgent):
    """
    Content Enricher Agent
    
    Adds metadata, performs trust analysis, and enriches content
    with additional context.
    """
    
    name = "enricher"
    version = "1.0.0"
    
    async def process(self, context: AgentContext) -> AgentResult:
        """Enrich content with additional analysis and metadata"""
        try:
            enrichments = {}
            
            if context.content_type == "tool":
                # Wrapper analysis for tools
                wrapper_analysis = await self._analyze_wrapper_status(context)
                enrichments["wrapper_analysis"] = wrapper_analysis
                
                # Calculate preliminary trust score
                trust_score = await self._calculate_trust_score(context, wrapper_analysis)
                enrichments["trust_score"] = trust_score
            
            # Vertical classification for both tools and news
            classification = await self._classify_vertical(context)
            enrichments["classification"] = classification
            
            # Store enrichments in context
            context.metadata["enrichments"] = enrichments
            
            # Update processed content with enrichments
            if context.processed_content:
                context.processed_content.update({
                    "wrapper_status": enrichments.get("wrapper_analysis", {}).get("wrapper_status", "unknown"),
                    "trust_score": enrichments.get("trust_score", {}).get("total", 0),
                    "vertical": classification.get("primary_vertical", "general"),
                    "categories": classification.get("categories", []),
                })
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                output=enrichments,
            )
            
        except Exception as e:
            self.logger.error("Enrichment failed", error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
            )
    
    async def _analyze_wrapper_status(self, context: AgentContext) -> Dict[str, Any]:
        """Analyze if a tool is a wrapper"""
        client, model = self.get_llm_client()
        
        # Prepare tool information
        tool_info = self._prepare_tool_info(context)
        
        prompt = WRAPPER_ANALYSIS_PROMPT.format(tool_info=tool_info)
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI systems analyst. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _calculate_trust_score(
        self,
        context: AgentContext,
        wrapper_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate preliminary trust score.
        
        Trust Score = (0.30 * Proprietary) + (0.40 * Reliability) + (0.15 * Transparency) + (0.15 * Liveness)
        """
        # Proprietary Tech Score (based on wrapper analysis)
        wrapper_likelihood = wrapper_analysis.get("wrapper_likelihood", 50)
        proprietary = 100 - wrapper_likelihood  # Inverse relationship
        
        # Reliability Score (placeholder - would need actual testing)
        reliability = 70  # Default until we can run actual tests
        
        # Transparency Score (based on signals)
        signals = wrapper_analysis.get("signals", {})
        transparency = 0
        if signals.get("has_custom_model"):
            transparency += 25
        if signals.get("has_proprietary_data"):
            transparency += 25
        if signals.get("has_enterprise_features"):
            transparency += 25
        if signals.get("sustainable_pricing"):
            transparency += 25
        
        # Liveness Score (placeholder - would check if tool is active)
        liveness = 80  # Default
        
        # Calculate weighted total
        total = (
            proprietary * 0.30 +
            reliability * 0.40 +
            transparency * 0.15 +
            liveness * 0.15
        )
        
        return {
            "total": round(total),
            "breakdown": {
                "proprietary": round(proprietary),
                "reliability": round(reliability),
                "transparency": round(transparency),
                "liveness": round(liveness),
            },
            "confidence": wrapper_analysis.get("confidence", 50),
            "is_preliminary": True,
        }
    
    async def _classify_vertical(self, context: AgentContext) -> Dict[str, Any]:
        """Classify content into verticals and categories"""
        client, model = self.get_llm_client()
        
        # Prepare content for classification
        content = self._prepare_content_for_classification(context)
        
        prompt = VERTICAL_CLASSIFICATION_PROMPT.format(content=content)
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a content classifier. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _prepare_tool_info(self, context: AgentContext) -> str:
        """Prepare tool information for analysis"""
        parts = []
        
        if context.processed_content:
            pc = context.processed_content
            parts.append(f"Name: {pc.get('title', 'Unknown')}")
            parts.append(f"Description: {pc.get('description', 'N/A')}")
            parts.append(f"Long Description: {pc.get('long_description', 'N/A')}")
            parts.append(f"Features: {', '.join(pc.get('features', []))}")
            parts.append(f"Pricing: {pc.get('pricing_info', 'Unknown')}")
        
        if context.source_url:
            parts.append(f"URL: {context.source_url}")
        
        if context.raw_content:
            parts.append(f"Raw Content: {context.raw_content[:2000]}")
        
        return "\n".join(parts)
    
    def _prepare_content_for_classification(self, context: AgentContext) -> str:
        """Prepare content for vertical classification"""
        parts = []
        
        if context.processed_content:
            pc = context.processed_content
            parts.append(f"Title: {pc.get('title', 'Unknown')}")
            parts.append(f"Description: {pc.get('description', 'N/A')}")
            if pc.get('features'):
                parts.append(f"Features: {', '.join(pc.get('features', []))}")
            if pc.get('content'):
                parts.append(f"Content: {pc.get('content', '')[:1000]}")
        
        return "\n".join(parts)

