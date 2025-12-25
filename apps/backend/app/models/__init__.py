"""
Data models for aboutai backend
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class WrapperStatus(str, Enum):
    """Classification of AI tool wrapper status"""
    NATIVE = "native"
    FINE_TUNED = "fine_tuned"
    RAG = "rag"
    WRAPPER = "wrapper"
    UNKNOWN = "unknown"


class Vertical(str, Enum):
    """Industry verticals"""
    AGTECH = "agtech"
    LEGAL = "legal"
    DEVTOOLS = "devtools"
    MARKETING = "marketing"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    GENERAL = "general"


class ContentStatus(str, Enum):
    """Content lifecycle status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class PricingType(str, Enum):
    """Pricing model types"""
    FREE = "free"
    FREEMIUM = "freemium"
    PAID = "paid"
    ENTERPRISE = "enterprise"


# ===========================================
# Tool Models
# ===========================================

class ToolPricing(BaseModel):
    """Pricing information for a tool"""
    type: PricingType = PricingType.FREEMIUM
    starting_price: Optional[float] = None
    currency: str = "USD"
    billing_period: Optional[str] = None  # monthly, yearly, one-time


class ToolData(BaseModel):
    """Complete tool data model matching frontend MDX schema"""
    # Core fields
    name: str
    slug: str
    description: str
    url: HttpUrl
    logo_url: Optional[str] = None
    
    # Classification
    vertical: Vertical = Vertical.GENERAL
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Trust Engine data
    trust_score: int = Field(ge=0, le=100, default=50)
    wrapper_status: WrapperStatus = WrapperStatus.UNKNOWN
    wrapper_likelihood: int = Field(ge=0, le=100, default=50)
    is_verified: bool = False
    
    # Trust analysis details
    proprietary_tech_score: int = Field(ge=0, le=100, default=50)
    reliability_score: int = Field(ge=0, le=100, default=50)
    transparency_score: int = Field(ge=0, le=100, default=50)
    liveness_score: int = Field(ge=0, le=100, default=50)
    
    # Detection signals
    signals: Dict[str, bool] = Field(default_factory=dict)
    detected_technologies: List[str] = Field(default_factory=list)
    api_dependencies: List[str] = Field(default_factory=list)
    
    # Pricing
    pricing: ToolPricing = Field(default_factory=ToolPricing)
    
    # Content
    content: str = ""  # MDX content body
    raw_content: str = ""  # Original scraped content
    
    # Metadata
    last_audited_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Pipeline tracking
    pipeline_id: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class ToolDraft(BaseModel):
    """Draft tool listing pending review"""
    id: str
    tool_data: ToolData
    status: ContentStatus = ContentStatus.DRAFT
    quality_score: float = 0.0
    reviewer_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================================
# News Models
# ===========================================

class NewsData(BaseModel):
    """Complete news article data model matching frontend MDX schema"""
    # Core fields
    title: str
    slug: str
    excerpt: str
    content: str = ""  # MDX content body
    
    # Author and source
    author: str = "aboutai Team"
    source_url: Optional[str] = None
    
    # Classification
    vertical: Vertical = Vertical.GENERAL
    tags: List[str] = Field(default_factory=list)
    
    # Hype analysis
    hype_score: int = Field(ge=0, le=100, default=50)  # Lower is better
    sensationalism_signals: List[str] = Field(default_factory=list)
    factual_signals: List[str] = Field(default_factory=list)
    
    # Media
    cover_image: Optional[str] = None
    
    # Status
    status: ContentStatus = ContentStatus.DRAFT
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Citations
    citations: List[str] = Field(default_factory=list)
    
    # Pipeline tracking
    pipeline_id: Optional[str] = None
    source: Optional[str] = None
    raw_content: str = ""


class NewsDraft(BaseModel):
    """Draft news article pending review"""
    id: str
    news_data: NewsData
    status: ContentStatus = ContentStatus.DRAFT
    quality_score: float = 0.0
    reviewer_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================================
# Pipeline Models
# ===========================================

class PipelineRun(BaseModel):
    """Tracks a content pipeline execution"""
    id: str
    status: str = "started"
    stage: str = "init"
    progress: float = 0.0
    
    # Results
    news_processed: int = 0
    tools_processed: int = 0
    errors: List[str] = Field(default_factory=list)
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ScrapedItem(BaseModel):
    """Raw scraped item from any source"""
    source: str
    source_type: str
    category: str  # news, tools, research
    vertical: str = "general"
    
    title: str
    url: str
    description: str = ""
    
    # Additional metadata
    published_at: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Source-specific fields
    extra: Dict[str, Any] = Field(default_factory=dict)


# ===========================================
# API Models
# ===========================================

class AnalyzeToolRequest(BaseModel):
    """Request to analyze a tool URL"""
    url: HttpUrl
    priority: str = "normal"
    force_refresh: bool = False


class AnalyzeToolResponse(BaseModel):
    """Response from tool analysis"""
    task_id: str
    status: str
    url: str
    message: str


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    categories: Optional[List[str]] = None
    verticals: Optional[List[str]] = None
    limit: int = 20


class SearchResult(BaseModel):
    """Search result item"""
    title: str
    url: str
    description: str
    source: str
    score: Optional[float] = None
    vertical: Optional[str] = None
