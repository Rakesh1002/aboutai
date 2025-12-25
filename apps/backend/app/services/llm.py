"""
LLM Service
Unified interface for Anthropic Claude and OpenAI models.
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import structlog

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import settings

logger = structlog.get_logger()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON output."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or settings.ANTHROPIC_MODEL
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        self.llm = ChatAnthropic(
            model=self.model,
            anthropic_api_key=self.api_key,
            max_tokens=4096,
        )
        logger.info("Initialized Anthropic provider", model=self.model)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text using Claude."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await self.llm.ainvoke(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate JSON output using Claude."""
        json_system = system_prompt or ""
        json_system += "\n\nYou must respond with valid JSON only. No other text."
        
        if schema:
            json_system += f"\n\nJSON Schema:\n{schema}"
        
        response = await self.generate(
            prompt,
            system_prompt=json_system,
            temperature=0.3,  # Lower temperature for structured output
        )
        
        # Parse JSON from response
        import json
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from Claude response", error=str(e))
            raise ValueError(f"Invalid JSON response: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, model: str = None, api_key: str = None):
        self.model = model or settings.OPENAI_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
        )
        logger.info("Initialized OpenAI provider", model=self.model)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text using GPT."""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await self.llm.ainvoke(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate JSON output using GPT with JSON mode."""
        json_system = system_prompt or ""
        json_system += "\n\nRespond with valid JSON only."
        
        if schema:
            json_system += f"\n\nFollow this JSON schema:\n{schema}"
        
        # Use JSON mode for OpenAI
        llm_json = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        
        messages = [
            SystemMessage(content=json_system),
            HumanMessage(content=prompt),
        ]
        
        response = await llm_json.ainvoke(messages, temperature=0.3)
        
        import json
        return json.loads(response.content)


class LLMService:
    """
    Unified LLM service that selects provider based on configuration.
    Prefers Anthropic Claude when available.
    """
    
    _instance: Optional["LLMService"] = None
    
    def __init__(self):
        self.provider: Optional[LLMProvider] = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the LLM provider based on config."""
        # Prefer Anthropic if configured
        if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                self.provider = AnthropicProvider()
                logger.info("Using Anthropic Claude as LLM provider")
                return
            except Exception as e:
                logger.warning("Failed to initialize Anthropic", error=str(e))
        
        # Fall back to OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.provider = OpenAIProvider()
                logger.info("Using OpenAI as LLM provider")
                return
            except Exception as e:
                logger.warning("Failed to initialize OpenAI", error=str(e))
        
        logger.error("No LLM provider available! Configure ANTHROPIC_API_KEY or OPENAI_API_KEY")
    
    @classmethod
    def get_instance(cls) -> "LLMService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = LLMService()
        return cls._instance
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text completion."""
        if not self.provider:
            raise RuntimeError("No LLM provider configured")
        
        return await self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON output."""
        if not self.provider:
            raise RuntimeError("No LLM provider configured")
        
        return await self.provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            schema=schema,
        )
    
    async def analyze_tool(self, scraped_content: str, url: str) -> Dict[str, Any]:
        """
        Analyze a scraped tool page and extract structured data.
        Returns tool metadata and trust analysis.
        """
        system_prompt = """You are an expert AI tool analyst for aboutai.com.
Your job is to analyze AI tools and determine:
1. Whether they are genuine AI tools or thin wrappers around foundation APIs
2. Their key features, pricing, and use cases
3. A trust score based on transparency, reliability, and proprietary value

Be skeptical but fair. Look for:
- Technical signals (custom models, fine-tuning, RAG, vector DBs)
- Transparency (team page, model disclosure, pricing clarity)
- Reliability indicators (uptime mentions, error handling, testimonials)
"""

        prompt = f"""Analyze this AI tool and provide structured data.

URL: {url}

Scraped Content:
{scraped_content[:15000]}  # Limit content length

Provide your analysis as JSON with this structure:
{{
    "title": "Tool name",
    "description": "Brief description (1-2 sentences)",
    "category": "One of: chatbot, code-assistant, image-generator, writing, productivity, analytics, automation, other",
    "pricing": "One of: free, freemium, paid, enterprise, unknown",
    "features": ["feature1", "feature2", "feature3"],
    "use_cases": ["use case 1", "use case 2"],
    "wrapper_analysis": {{
        "is_wrapper": true/false,
        "wrapper_status": "native|fine_tuned|rag|wrapper|unknown",
        "confidence": 0.0-1.0,
        "signals": {{
            "has_custom_model": true/false,
            "has_fine_tuning": true/false,
            "has_vector_db": true/false,
            "has_proprietary_data": true/false,
            "discloses_model": true/false,
            "direct_api_dependency": true/false
        }},
        "reasoning": "Brief explanation"
    }},
    "trust_analysis": {{
        "trust_score": 0-100,
        "proprietary_score": 0-100,
        "reliability_score": 0-100,
        "transparency_score": 0-100,
        "reasoning": "Brief explanation"
    }},
    "tags": ["tag1", "tag2", "tag3"]
}}"""

        return await self.generate_json(prompt, system_prompt=system_prompt)
    
    async def analyze_news(self, content: str, title: str, source: str) -> Dict[str, Any]:
        """
        Analyze a news article for hype and extract key information.
        """
        system_prompt = """You are an AI news analyst for aboutai.com.
Your job is to analyze AI news articles and determine:
1. The actual factual content vs marketing hype
2. Key takeaways and implications
3. A "hype score" measuring sensationalism

Be objective. Look for:
- Unverified claims or speculation
- Buzzwords without substance
- Actual technical details or announcements
- Sources and citations
"""

        prompt = f"""Analyze this AI news article.

Title: {title}
Source: {source}

Content:
{content[:10000]}

Provide your analysis as JSON:
{{
    "summary": "2-3 sentence factual summary",
    "key_points": ["point 1", "point 2", "point 3"],
    "hype_analysis": {{
        "hype_score": 0-100,
        "hype_indicators": ["indicator 1", "indicator 2"],
        "factual_indicators": ["fact 1", "fact 2"],
        "reasoning": "Brief explanation"
    }},
    "vertical": "One of: general, agtech, legal, devtools, marketing, healthcare, finance, other",
    "tags": ["tag1", "tag2", "tag3"],
    "sentiment": "positive|negative|neutral"
}}"""

        return await self.generate_json(prompt, system_prompt=system_prompt)
    
    async def generate_tool_content(self, tool_data: Dict[str, Any]) -> str:
        """
        Generate MDX content for a tool listing page.
        """
        system_prompt = """You are a technical writer for aboutai.com.
Write concise, informative content about AI tools.
Use markdown formatting. Be objective and fact-based.
Include our trust analysis prominently.
"""

        prompt = f"""Generate MDX content for this AI tool listing.

Tool Data:
{tool_data}

Write the content in this format:

---
title: [Tool Name]
slug: [slug]
description: [Brief description]
category: [category]
pricing: [pricing]
url: [url]
trustScore: [0-100]
wrapperStatus: [status]
tags: [array]
publishedAt: [ISO date]
---

# [Tool Name]

[2-3 paragraph overview]

## Key Features

- Feature 1
- Feature 2
- Feature 3

## Trust Analysis

[Explain our trust score and wrapper analysis findings]

## Pricing

[Pricing information]

## Who Should Use This

[Target audience]
"""

        return await self.generate(prompt, system_prompt=system_prompt)


# Convenience function
def get_llm_service() -> LLMService:
    """Get the LLM service instance."""
    return LLMService.get_instance()

