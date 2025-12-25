"""
Trust Engine - Autonomous AI agent for tool verification and wrapper detection.
This is the core differentiator of aboutai.

Trust Score Algorithm:
  TrustScore = (w1 × P_tech) + (w2 × R_test) + (w3 × T_trans) + (w4 × L_life)

Where:
  P_tech = Proprietary Technology Score (0-100)
  R_test = Reliability/Testing Score (0-100)  
  T_trans = Transparency Score (0-100)
  L_life = Liveness/Activity Score (0-100)

Weights:
  w1 = 0.30 (Proprietary Tech)
  w2 = 0.40 (Reliability)
  w3 = 0.15 (Transparency)
  w4 = 0.15 (Liveness)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json
from datetime import datetime, timedelta
import structlog
import asyncio

from app.core.config import settings
from app.agents.scraper.browser import browser_pool, scrape_with_browser

logger = structlog.get_logger()


class WrapperStatus(Enum):
    """Classification of AI tool wrapper status"""
    NATIVE = "native"           # 0-20% wrapper likelihood: Custom models, proprietary R&D
    FINE_TUNED = "fine_tuned"   # 21-40%: Domain-specific fine-tuning
    RAG = "rag"                 # 41-60%: Proprietary knowledge bases (RAG)
    LIGHT_WRAPPER = "wrapper"   # 61-80%: Meaningful UX over APIs
    PURE_WRAPPER = "wrapper"    # 81-100%: Simple UI over GPT/Claude


@dataclass
class TrustAnalysis:
    """Result of trust analysis for an AI tool"""
    url: str
    name: str
    
    # Overall scores
    trust_score: int  # 0-100
    wrapper_likelihood: int  # 0-100 (higher = more likely wrapper)
    wrapper_status: WrapperStatus
    
    # Component scores
    proprietary_tech_score: int  # P_tech
    reliability_score: int  # R_test
    transparency_score: int  # T_trans
    liveness_score: int  # L_life
    
    # Detection signals
    signals: Dict[str, bool] = field(default_factory=dict)
    
    # Evidence
    detected_technologies: List[str] = field(default_factory=list)
    api_dependencies: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    # Metadata
    analyzed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.0


@dataclass
class HypeAnalysis:
    """Result of hype/sensationalism analysis for news content"""
    hype_score: int  # 0-100 (lower is better, more factual)
    sensationalism_signals: List[str] = field(default_factory=list)
    factual_signals: List[str] = field(default_factory=list)
    reasoning: str = ""


class TrustEngine:
    """
    Autonomous Trust Engine for AI tool verification.
    Uses open source tools and LLMs for analysis.
    """
    
    # Weights for trust score calculation
    WEIGHT_TECH = 0.30
    WEIGHT_RELIABILITY = 0.40
    WEIGHT_TRANSPARENCY = 0.15
    WEIGHT_LIVENESS = 0.15
    
    # Known API providers (wrappers typically depend on these)
    KNOWN_API_PROVIDERS = {
        "openai.com": "OpenAI",
        "api.openai.com": "OpenAI",
        "anthropic.com": "Anthropic",
        "api.anthropic.com": "Anthropic",
        "ai.google.dev": "Google AI",
        "generativelanguage.googleapis.com": "Google AI",
        "api.cohere.ai": "Cohere",
        "api.mistral.ai": "Mistral",
        "api.together.xyz": "Together AI",
        "api.replicate.com": "Replicate",
    }
    
    # Technologies that indicate proprietary work
    PROPRIETARY_INDICATORS = [
        "vector database", "pinecone", "weaviate", "qdrant", "milvus", "chromadb",
        "fine-tuned", "fine tuned", "custom model", "proprietary model",
        "training data", "trained on", "our model", "in-house",
        "embeddings", "rag", "retrieval augmented",
        "langchain", "llamaindex", "semantic search",
    ]
    
    # Wrapper indicators
    WRAPPER_INDICATORS = [
        "powered by gpt", "powered by chatgpt", "uses gpt-4", "uses claude",
        "openai api", "anthropic api", "gpt wrapper", "chatgpt wrapper",
        "built on gpt", "built on claude", "simple interface",
        "no coding required", "just prompts",
    ]
    
    # Hype words for news analysis
    HYPE_WORDS = [
        "revolutionary", "game-changing", "groundbreaking", "disruptive",
        "agi", "superintelligence", "conscious", "sentient", "magic",
        "best ever", "unbelievable", "incredible", "amazing",
        "will replace", "end of", "death of", "kills",
        "breakthrough", "first ever", "world's first",
    ]
    
    # Factual indicators
    FACTUAL_INDICATORS = [
        "benchmark", "evaluation", "measured", "tested", "compared",
        "researchers", "paper", "published", "peer-reviewed",
        "according to", "study shows", "data indicates",
        "limitations", "challenges", "concerns", "risks",
    ]
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_tool(self, url: str, name: str = None) -> TrustAnalysis:
        """
        Perform comprehensive trust analysis on an AI tool.
        """
        logger.info("Starting trust analysis", url=url)
        
        # Fetch and analyze the tool's website
        page_content, page_html = await self._fetch_page(url)
        
        # Extract name if not provided
        if not name:
            name = await self._extract_tool_name(page_html, url)
        
        # Run all analysis components in parallel
        tasks = [
            self._analyze_proprietary_tech(url, page_content, page_html),
            self._analyze_transparency(page_content, page_html, url),
            self._analyze_liveness(url, page_html),
        ]
        
        results = await asyncio.gather(*tasks)
        
        tech_score, tech_signals, detected_tech, api_deps = results[0]
        trans_score, trans_signals = results[1]
        live_score, live_signals = results[2]
        
        # Reliability score (would need actual testing in production)
        reliability_score = 70  # Default placeholder
        
        # Combine all signals
        all_signals = {**tech_signals, **trans_signals, **live_signals}
        
        # Calculate wrapper likelihood
        wrapper_likelihood = self._calculate_wrapper_likelihood(all_signals, api_deps)
        
        # Calculate trust score
        trust_score = int(
            (tech_score * self.WEIGHT_TECH) +
            (reliability_score * self.WEIGHT_RELIABILITY) +
            (trans_score * self.WEIGHT_TRANSPARENCY) +
            (live_score * self.WEIGHT_LIVENESS)
        )
        
        # Adjust trust score based on wrapper likelihood
        if wrapper_likelihood > 80:
            trust_score = max(20, trust_score - 30)
        elif wrapper_likelihood > 60:
            trust_score = max(30, trust_score - 20)
        
        # Determine wrapper status
        wrapper_status = self._determine_wrapper_status(wrapper_likelihood)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            all_signals, detected_tech, api_deps, wrapper_likelihood
        )
        
        analysis = TrustAnalysis(
            url=url,
            name=name,
            trust_score=min(100, max(0, trust_score)),
            wrapper_likelihood=wrapper_likelihood,
            wrapper_status=wrapper_status,
            proprietary_tech_score=tech_score,
            reliability_score=reliability_score,
            transparency_score=trans_score,
            liveness_score=live_score,
            signals=all_signals,
            detected_technologies=detected_tech,
            api_dependencies=api_deps,
            reasoning=reasoning,
            confidence=0.75 if page_content else 0.3,
        )
        
        logger.info(
            "Trust analysis complete",
            url=url,
            trust_score=trust_score,
            wrapper_status=wrapper_status.value,
        )
        
        return analysis
    
    async def _fetch_page(self, url: str) -> Tuple[str, str]:
        """Fetch page content using HTTP client"""
        try:
            response = await self.client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                follow_redirects=True,
            )
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            return text.lower(), html
            
        except Exception as e:
            logger.error("Failed to fetch page", url=url, error=str(e))
            return "", ""
    
    async def _extract_tool_name(self, html: str, url: str) -> str:
        """Extract tool name from page"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Try meta title
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
                # Clean up common suffixes
                for suffix in [" - ", " | ", " – ", " : "]:
                    if suffix in title:
                        title = title.split(suffix)[0]
                return title[:100]
            
            # Try og:title
            og_title = soup.find("meta", property="og:title")
            if og_title:
                return og_title.get("content", "")[:100]
            
            # Fallback to domain
            return urlparse(url).netloc.replace("www.", "")
            
        except:
            return urlparse(url).netloc.replace("www.", "")
    
    async def _analyze_proprietary_tech(
        self, url: str, content: str, html: str
    ) -> Tuple[int, Dict[str, bool], List[str], List[str]]:
        """
        Analyze proprietary technology indicators.
        Returns: (score, signals, detected_tech, api_dependencies)
        """
        signals = {
            "has_vector_db": False,
            "has_fine_tuning": False,
            "has_custom_model": False,
            "has_rag_pipeline": False,
            "has_embeddings": False,
            "discloses_api_dependency": False,
        }
        
        detected_tech = []
        api_deps = []
        score = 50  # Start at 50
        
        # Check for proprietary indicators
        content_lower = content.lower() if content else ""
        
        for indicator in self.PROPRIETARY_INDICATORS:
            if indicator in content_lower:
                if "vector" in indicator or "pinecone" in indicator or "weaviate" in indicator:
                    signals["has_vector_db"] = True
                    detected_tech.append(indicator)
                    score += 10
                elif "fine" in indicator:
                    signals["has_fine_tuning"] = True
                    detected_tech.append(indicator)
                    score += 15
                elif "custom" in indicator or "proprietary" in indicator:
                    signals["has_custom_model"] = True
                    detected_tech.append(indicator)
                    score += 20
                elif "rag" in indicator or "retrieval" in indicator:
                    signals["has_rag_pipeline"] = True
                    detected_tech.append(indicator)
                    score += 10
                elif "embedding" in indicator:
                    signals["has_embeddings"] = True
                    detected_tech.append(indicator)
                    score += 5
        
        # Check for wrapper indicators (negative score)
        for indicator in self.WRAPPER_INDICATORS:
            if indicator in content_lower:
                score -= 15
                signals["discloses_api_dependency"] = True
        
        # Check for known API providers in HTML (network analysis)
        if html:
            for provider_domain, provider_name in self.KNOWN_API_PROVIDERS.items():
                if provider_domain in html.lower():
                    api_deps.append(provider_name)
                    if not signals["has_custom_model"] and not signals["has_fine_tuning"]:
                        score -= 10
        
        # Normalize score
        score = min(100, max(0, score))
        
        return score, signals, list(set(detected_tech)), list(set(api_deps))
    
    async def _analyze_transparency(
        self, content: str, html: str, url: str
    ) -> Tuple[int, Dict[str, bool]]:
        """
        Analyze transparency indicators.
        """
        signals = {
            "has_pricing_page": False,
            "has_about_page": False,
            "has_team_page": False,
            "has_docs": False,
            "has_privacy_policy": False,
            "has_terms": False,
            "discloses_model": False,
        }
        
        score = 30  # Start low
        content_lower = content.lower() if content else ""
        html_lower = html.lower() if html else ""
        
        # Check for transparency indicators in links
        transparency_keywords = {
            "pricing": ("has_pricing_page", 15),
            "about": ("has_about_page", 10),
            "team": ("has_team_page", 10),
            "documentation": ("has_docs", 10),
            "docs": ("has_docs", 10),
            "privacy": ("has_privacy_policy", 10),
            "terms": ("has_terms", 5),
        }
        
        for keyword, (signal, points) in transparency_keywords.items():
            if keyword in html_lower:
                signals[signal] = True
                score += points
        
        # Check for model disclosure
        model_keywords = ["gpt-4", "gpt-3.5", "claude", "llama", "mistral", "gemini"]
        for model in model_keywords:
            if model in content_lower:
                signals["discloses_model"] = True
                score += 10
                break
        
        return min(100, score), signals
    
    async def _analyze_liveness(
        self, url: str, html: str
    ) -> Tuple[int, Dict[str, bool]]:
        """
        Analyze liveness/activity indicators.
        """
        signals = {
            "has_recent_updates": False,
            "has_blog": False,
            "has_changelog": False,
            "has_social_presence": False,
            "is_active": True,  # Assume active if reachable
        }
        
        score = 50
        html_lower = html.lower() if html else ""
        
        # Check for activity indicators
        if "blog" in html_lower or "news" in html_lower:
            signals["has_blog"] = True
            score += 15
        
        if "changelog" in html_lower or "updates" in html_lower:
            signals["has_changelog"] = True
            score += 15
        
        if "twitter" in html_lower or "linkedin" in html_lower:
            signals["has_social_presence"] = True
            score += 10
        
        # Check for copyright year (indicates maintenance)
        current_year = str(datetime.now().year)
        if current_year in html_lower:
            signals["has_recent_updates"] = True
            score += 10
        
        return min(100, score), signals
    
    def _calculate_wrapper_likelihood(
        self, signals: Dict[str, bool], api_deps: List[str]
    ) -> int:
        """Calculate wrapper likelihood percentage"""
        likelihood = 50  # Start neutral
        
        # Negative indicators (more wrapper-like)
        if api_deps:
            likelihood += 20
        if signals.get("discloses_api_dependency"):
            likelihood += 15
        
        # Positive indicators (less wrapper-like)
        if signals.get("has_custom_model"):
            likelihood -= 30
        if signals.get("has_fine_tuning"):
            likelihood -= 25
        if signals.get("has_vector_db"):
            likelihood -= 15
        if signals.get("has_rag_pipeline"):
            likelihood -= 10
        if signals.get("has_embeddings"):
            likelihood -= 5
        
        return min(100, max(0, likelihood))
    
    def _determine_wrapper_status(self, likelihood: int) -> WrapperStatus:
        """Determine wrapper status from likelihood"""
        if likelihood <= 20:
            return WrapperStatus.NATIVE
        elif likelihood <= 40:
            return WrapperStatus.FINE_TUNED
        elif likelihood <= 60:
            return WrapperStatus.RAG
        else:
            return WrapperStatus.LIGHT_WRAPPER
    
    def _generate_reasoning(
        self,
        signals: Dict[str, bool],
        detected_tech: List[str],
        api_deps: List[str],
        wrapper_likelihood: int,
    ) -> str:
        """Generate human-readable reasoning for the analysis"""
        reasons = []
        
        if wrapper_likelihood > 60:
            reasons.append(f"High wrapper likelihood ({wrapper_likelihood}%).")
            if api_deps:
                reasons.append(f"Detected API dependencies: {', '.join(api_deps)}.")
        else:
            reasons.append(f"Low wrapper likelihood ({wrapper_likelihood}%).")
        
        if detected_tech:
            reasons.append(f"Proprietary tech indicators: {', '.join(detected_tech[:5])}.")
        
        if signals.get("has_custom_model"):
            reasons.append("Evidence of custom/proprietary model.")
        if signals.get("has_fine_tuning"):
            reasons.append("Evidence of fine-tuning.")
        if signals.get("has_vector_db"):
            reasons.append("Uses vector database for RAG.")
        
        if not signals.get("has_pricing_page"):
            reasons.append("No clear pricing information found.")
        if not signals.get("has_docs"):
            reasons.append("Limited documentation available.")
        
        return " ".join(reasons)
    
    async def analyze_hype(self, content: str, title: str = "") -> HypeAnalysis:
        """
        Analyze news content for hype/sensationalism.
        Returns a hype score (0-100, lower is better).
        """
        text = f"{title} {content}".lower()
        
        hype_signals = []
        factual_signals = []
        
        # Check for hype words
        for word in self.HYPE_WORDS:
            if word in text:
                hype_signals.append(word)
        
        # Check for factual indicators
        for indicator in self.FACTUAL_INDICATORS:
            if indicator in text:
                factual_signals.append(indicator)
        
        # Calculate hype score
        hype_count = len(hype_signals)
        factual_count = len(factual_signals)
        
        # Base score on ratio of hype to factual
        if factual_count > 0:
            ratio = hype_count / (hype_count + factual_count)
            hype_score = int(ratio * 100)
        else:
            # No factual indicators, score based on hype count
            hype_score = min(100, hype_count * 15)
        
        # Generate reasoning
        reasoning_parts = []
        if hype_signals:
            reasoning_parts.append(f"Hype indicators found: {', '.join(hype_signals[:5])}")
        if factual_signals:
            reasoning_parts.append(f"Factual indicators: {', '.join(factual_signals[:5])}")
        
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Neutral tone detected."
        
        return HypeAnalysis(
            hype_score=hype_score,
            sensationalism_signals=hype_signals[:10],
            factual_signals=factual_signals[:10],
            reasoning=reasoning,
        )


# ===========================================
# Vertical Classifier
# ===========================================

class VerticalClassifier:
    """
    Classifies AI tools and news into industry verticals.
    """
    
    VERTICAL_KEYWORDS = {
        "agtech": [
            "agriculture", "farming", "crop", "livestock", "harvest",
            "soil", "irrigation", "precision farming", "agri",
            "food production", "yield", "sustainable farming",
        ],
        "legal": [
            "legal", "law firm", "attorney", "lawyer", "contract",
            "litigation", "compliance", "regulatory", "court",
            "discovery", "paralegal", "legal tech", "jurisprudence",
        ],
        "devtools": [
            "developer", "code", "programming", "api", "sdk",
            "github", "debugging", "testing", "deployment",
            "infrastructure", "devops", "software development",
            "ide", "compiler", "framework", "library",
        ],
        "marketing": [
            "marketing", "advertising", "seo", "content creation",
            "social media", "campaign", "brand", "copywriting",
            "analytics", "conversion", "lead generation",
            "email marketing", "digital marketing",
        ],
        "healthcare": [
            "healthcare", "medical", "health", "patient", "clinical",
            "diagnosis", "treatment", "pharma", "biotech",
            "hospital", "doctor", "nursing", "telemedicine",
        ],
        "finance": [
            "finance", "banking", "investment", "trading", "fintech",
            "insurance", "accounting", "tax", "portfolio",
            "cryptocurrency", "blockchain", "payment",
        ],
    }
    
    def classify(self, content: str, title: str = "") -> str:
        """
        Classify content into a vertical.
        Returns the best matching vertical or 'general'.
        """
        text = f"{title} {content}".lower()
        
        scores = {}
        for vertical, keywords in self.VERTICAL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[vertical] = score
        
        if not scores:
            return "general"
        
        return max(scores, key=scores.get)
    
    def get_all_verticals(self) -> List[str]:
        """Get list of all supported verticals"""
        return list(self.VERTICAL_KEYWORDS.keys()) + ["general"]

