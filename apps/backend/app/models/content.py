"""
Content data models for tools and news articles
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class WrapperStatus(str, Enum):
    NATIVE = "native"
    FINE_TUNED = "fine_tuned"
    RAG = "rag"
    WRAPPER = "wrapper"
    UNKNOWN = "unknown"


class Vertical(str, Enum):
    AGTECH = "agtech"
    LEGAL = "legal"
    DEVTOOLS = "devtools"
    MARKETING = "marketing"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    GENERAL = "general"


class Citation(BaseModel):
    """Source citation for content"""
    url: str
    title: str
    source_name: str
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    snippet: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None


class ContentMetadata(BaseModel):
    """Metadata for scraped/generated content"""
    source_urls: List[str] = []
    citations: List[Citation] = []
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    agent_versions: Dict[str, str] = {}
    confidence_score: float = 0.0
    human_reviewed: bool = False


# ===========================================
# Tool Models
# ===========================================

class ToolPricing(BaseModel):
    """Pricing information for a tool"""
    model: str = "unknown"  # free, freemium, paid, enterprise
    starting_price: Optional[float] = None
    currency: str = "USD"
    billing_period: Optional[str] = None  # monthly, yearly, one-time
    free_tier: bool = False
    free_tier_limits: Optional[str] = None


class TrustScoreBreakdown(BaseModel):
    """Breakdown of trust score components"""
    proprietary_tech: float = 0.0  # 0-100
    reliability: float = 0.0  # 0-100
    transparency: float = 0.0  # 0-100
    liveness: float = 0.0  # 0-100
    
    @property
    def total(self) -> float:
        """Calculate weighted total trust score"""
        return (
            self.proprietary_tech * 0.30 +
            self.reliability * 0.40 +
            self.transparency * 0.15 +
            self.liveness * 0.15
        )


class Tool(BaseModel):
    """Published tool listing"""
    id: str
    slug: str
    title: str
    description: str
    url: HttpUrl
    logo_url: Optional[str] = None
    
    # Classification
    vertical: Vertical = Vertical.GENERAL
    categories: List[str] = []
    tags: List[str] = []
    
    # Trust Engine
    trust_score: int = 0
    trust_score_breakdown: Optional[TrustScoreBreakdown] = None
    wrapper_status: WrapperStatus = WrapperStatus.UNKNOWN
    is_verified: bool = False
    
    # Pricing
    pricing: Optional[ToolPricing] = None
    
    # Metadata
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_audited_at: Optional[datetime] = None
    
    # Content
    long_description: Optional[str] = None
    features: List[str] = []
    use_cases: List[str] = []
    
    # Metadata
    metadata: Optional[ContentMetadata] = None


class ToolDraft(BaseModel):
    """Tool listing draft pending review"""
    id: str
    tool_id: Optional[str] = None  # If updating existing tool
    status: ContentStatus = ContentStatus.DRAFT
    
    # Core fields
    title: str
    slug: str
    description: str
    url: str
    
    # Generated content
    long_description: Optional[str] = None
    features: List[str] = []
    use_cases: List[str] = []
    
    # Classification (suggested)
    suggested_vertical: Optional[Vertical] = None
    suggested_categories: List[str] = []
    suggested_tags: List[str] = []
    
    # Trust analysis (preliminary)
    preliminary_trust_score: Optional[int] = None
    wrapper_analysis: Optional[Dict[str, Any]] = None
    
    # Pipeline tracking
    pipeline_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)


# ===========================================
# News Models
# ===========================================

class NewsArticle(BaseModel):
    """Published news article"""
    id: str
    slug: str
    title: str
    description: str
    content: str  # MDX content
    
    # Classification
    vertical: Vertical = Vertical.GENERAL
    tags: List[str] = []
    
    # Metrics
    hype_score: int = 50  # 0-100
    
    # Source
    source_url: Optional[str] = None
    author: Optional[str] = None
    
    # Dates
    published_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Optional[ContentMetadata] = None


class NewsArticleDraft(BaseModel):
    """News article draft pending review"""
    id: str
    article_id: Optional[str] = None  # If updating existing article
    status: ContentStatus = ContentStatus.DRAFT
    
    # Core fields
    title: str
    slug: str
    description: str
    content: str  # MDX content
    
    # Classification (suggested)
    suggested_vertical: Optional[Vertical] = None
    suggested_tags: List[str] = []
    suggested_hype_score: Optional[int] = None
    
    # Pipeline tracking
    pipeline_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)


# ===========================================
# Scraped Content Model
# ===========================================

class ScrapedContent(BaseModel):
    """Raw scraped content before processing"""
    id: str
    source_url: str
    source_type: str  # "news", "directory", "social", "search"
    source_name: str
    
    # Raw content
    title: Optional[str] = None
    raw_text: str
    raw_html: Optional[str] = None
    
    # Extracted data
    extracted_urls: List[str] = []
    extracted_entities: List[str] = []
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    processing_error: Optional[str] = None

