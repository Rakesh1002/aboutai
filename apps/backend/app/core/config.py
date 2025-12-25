"""
Configuration settings for aboutai backend.
Uses Pydantic Settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ===========================================
    # Application
    # ===========================================
    APP_NAME: str = "aboutai Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # ===========================================
    # API Settings
    # ===========================================
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://aboutai.space"]
    
    # ===========================================
    # LLM Providers
    # ===========================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"
    
    # Default LLM provider (anthropic or openai)
    LLM_PROVIDER: str = "anthropic"
    
    # ===========================================
    # Supabase (Database)
    # ===========================================
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None  # anon/public key
    SUPABASE_SERVICE_KEY: Optional[str] = None  # service role key (backend only)
    
    # ===========================================
    # Upstash Redis (Task Queue & Cache)
    # ===========================================
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None
    # Standard Redis URL (for Celery)
    # If using Upstash, set this to: rediss://default:TOKEN@ENDPOINT:6379
    REDIS_URL: str = "redis://localhost:6379/0"
    
    @property
    def celery_broker_url(self) -> str:
        """Get Redis URL for Celery broker."""
        # If Upstash REST is configured, construct the Redis URL
        if self.UPSTASH_REDIS_REST_URL and self.UPSTASH_REDIS_REST_TOKEN:
            # Extract host from REST URL (https://xxx.upstash.io -> xxx.upstash.io)
            host = self.UPSTASH_REDIS_REST_URL.replace("https://", "").replace("http://", "")
            return f"rediss://default:{self.UPSTASH_REDIS_REST_TOKEN}@{host}:6379"
        return self.REDIS_URL
    
    # ===========================================
    # Self-Hosted Services
    # ===========================================
    # SearXNG (metasearch)
    SEARXNG_URL: str = "http://localhost:8080"
    
    # ===========================================
    # External APIs (Optional)
    # ===========================================
    GITHUB_TOKEN: Optional[str] = None  # For higher rate limits
    
    # ===========================================
    # Content Paths
    # ===========================================
    # Path to frontend content directory (MDX files)
    FRONTEND_CONTENT_DIR: str = str(
        Path(__file__).parent.parent.parent.parent / "frontend" / "content"
    )
    
    # Path to drafts directory
    DRAFTS_DIR: str = str(
        Path(__file__).parent.parent.parent / "data" / "drafts"
    )
    
    # Path to data directory
    DATA_DIR: str = str(
        Path(__file__).parent.parent.parent / "data"
    )
    
    # ===========================================
    # Pipeline Settings
    # ===========================================
    # Maximum items to process per pipeline run
    MAX_NEWS_PER_RUN: int = 50
    MAX_TOOLS_PER_RUN: int = 30
    
    # Minimum quality score for auto-approval (0.0-1.0)
    # Set lower for more automatic publishing, higher for stricter review
    AUTO_APPROVE_THRESHOLD: float = 0.5
    
    # Trust score thresholds
    TRUST_SCORE_MIN_PUBLISH: int = 30  # Minimum trust score to publish
    
    # ===========================================
    # Scheduling
    # ===========================================
    # Cron schedules for Celery Beat
    SCRAPE_NEWS_SCHEDULE: str = "0 */4 * * *"  # Every 4 hours
    SCRAPE_TOOLS_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    REFRESH_TRUST_SCORES_SCHEDULE: str = "0 */6 * * *"  # Every 6 hours
    PUBLISH_APPROVED_SCHEDULE: str = "0 * * * *"  # Every hour
    
    # ===========================================
    # Browser Automation
    # ===========================================
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000  # 30 seconds
    
    # ===========================================
    # Rate Limiting
    # ===========================================
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure directories exist
        Path(self.FRONTEND_CONTENT_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.DRAFTS_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.DATA_DIR).mkdir(parents=True, exist_ok=True)
        
        # Create content subdirectories
        (Path(self.FRONTEND_CONTENT_DIR) / "tools").mkdir(exist_ok=True)
        (Path(self.FRONTEND_CONTENT_DIR) / "news").mkdir(exist_ok=True)


# Create global settings instance
settings = Settings()
