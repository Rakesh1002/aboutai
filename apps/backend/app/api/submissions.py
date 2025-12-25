"""
User Submission API Routes
Allow users to submit AI tools for listing and review.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid
import structlog
import json
from pathlib import Path

from app.core.config import settings
from app.agents.trust_engine import TrustEngine, VerticalClassifier
from app.services.publisher import ContentDraftStore
from app.models import ToolData, ToolPricing, PricingType, Vertical, WrapperStatus

router = APIRouter(prefix="/submit", tags=["submissions"])
logger = structlog.get_logger()


# ===========================================
# Submission Models
# ===========================================

class ToolSubmission(BaseModel):
    """User-submitted tool listing request"""
    # Required fields
    name: str = Field(..., min_length=2, max_length=100)
    url: HttpUrl
    description: str = Field(..., min_length=20, max_length=1000)
    
    # Optional details
    logo_url: Optional[str] = None
    categories: List[str] = Field(default_factory=list, max_length=5)
    vertical: Optional[str] = None  # agtech, legal, devtools, marketing, general
    
    # Pricing
    pricing_type: str = "freemium"  # free, freemium, paid, enterprise
    pricing_amount: Optional[float] = None
    
    # Features
    features: List[str] = Field(default_factory=list, max_length=10)
    
    # Submitter info
    submitter_email: Optional[EmailStr] = None
    submitter_name: Optional[str] = None
    is_owner: bool = False  # Is the submitter the tool owner?
    
    # Additional context
    why_notable: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = None
    docs_url: Optional[str] = None


class NewsSubmission(BaseModel):
    """User-submitted news tip"""
    title: str = Field(..., min_length=5, max_length=200)
    url: HttpUrl
    summary: Optional[str] = Field(None, max_length=500)
    vertical: Optional[str] = None
    submitter_email: Optional[EmailStr] = None


class PodcastSubmission(BaseModel):
    """User-submitted podcast recommendation"""
    name: str = Field(..., min_length=2, max_length=100)
    rss_url: HttpUrl
    description: Optional[str] = Field(None, max_length=500)
    host: Optional[str] = None
    submitter_email: Optional[EmailStr] = None


class SubmissionResponse(BaseModel):
    """Response after submission"""
    submission_id: str
    status: str
    message: str
    estimated_review_time: str


# ===========================================
# Submission Storage
# ===========================================

class SubmissionStore:
    """Store and manage user submissions"""
    
    def __init__(self):
        self.submissions_dir = Path(settings.DATA_DIR) / "submissions"
        self.tools_dir = self.submissions_dir / "tools"
        self.news_dir = self.submissions_dir / "news"
        self.podcasts_dir = self.submissions_dir / "podcasts"
        
        # Ensure directories exist
        for d in [self.tools_dir, self.news_dir, self.podcasts_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def save_tool_submission(self, submission: ToolSubmission) -> str:
        """Save a tool submission"""
        submission_id = str(uuid.uuid4())
        
        data = {
            "id": submission_id,
            "type": "tool",
            "status": "pending",
            "data": submission.model_dump(mode="json"),
            "submitted_at": datetime.utcnow().isoformat(),
        }
        
        file_path = self.tools_dir / f"{submission_id}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info("Tool submission saved", submission_id=submission_id, name=submission.name)
        return submission_id
    
    def save_news_submission(self, submission: NewsSubmission) -> str:
        """Save a news submission"""
        submission_id = str(uuid.uuid4())
        
        data = {
            "id": submission_id,
            "type": "news",
            "status": "pending",
            "data": submission.model_dump(mode="json"),
            "submitted_at": datetime.utcnow().isoformat(),
        }
        
        file_path = self.news_dir / f"{submission_id}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return submission_id
    
    def save_podcast_submission(self, submission: PodcastSubmission) -> str:
        """Save a podcast submission"""
        submission_id = str(uuid.uuid4())
        
        data = {
            "id": submission_id,
            "type": "podcast",
            "status": "pending",
            "data": submission.model_dump(mode="json"),
            "submitted_at": datetime.utcnow().isoformat(),
        }
        
        file_path = self.podcasts_dir / f"{submission_id}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return submission_id
    
    def list_submissions(self, submission_type: str = None, status: str = None) -> List[dict]:
        """List all submissions"""
        submissions = []
        
        dirs = {
            "tool": self.tools_dir,
            "news": self.news_dir,
            "podcast": self.podcasts_dir,
        }
        
        if submission_type:
            search_dirs = {submission_type: dirs[submission_type]}
        else:
            search_dirs = dirs
        
        for stype, sdir in search_dirs.items():
            for file_path in sdir.glob("*.json"):
                with open(file_path) as f:
                    data = json.load(f)
                    if status is None or data.get("status") == status:
                        submissions.append(data)
        
        # Sort by submitted_at descending
        submissions.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        return submissions
    
    def get_submission(self, submission_id: str) -> Optional[dict]:
        """Get a specific submission"""
        for sdir in [self.tools_dir, self.news_dir, self.podcasts_dir]:
            file_path = sdir / f"{submission_id}.json"
            if file_path.exists():
                with open(file_path) as f:
                    return json.load(f)
        return None
    
    def update_status(self, submission_id: str, status: str, notes: str = None) -> bool:
        """Update submission status"""
        for sdir in [self.tools_dir, self.news_dir, self.podcasts_dir]:
            file_path = sdir / f"{submission_id}.json"
            if file_path.exists():
                with open(file_path) as f:
                    data = json.load(f)
                
                data["status"] = status
                data["updated_at"] = datetime.utcnow().isoformat()
                if notes:
                    data["reviewer_notes"] = notes
                
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2, default=str)
                
                return True
        return False


# ===========================================
# API Endpoints
# ===========================================

@router.post("/tool", response_model=SubmissionResponse)
async def submit_tool(
    submission: ToolSubmission,
    background_tasks: BackgroundTasks,
):
    """
    Submit an AI tool for listing.
    
    The tool will be:
    1. Queued for Trust Engine analysis
    2. Reviewed by our team
    3. Published if approved
    
    **Priority listing**: Tools submitted by owners (is_owner=true) with
    complete information get expedited review.
    """
    logger.info("Tool submission received", name=submission.name, url=str(submission.url))
    
    # Save submission
    store = SubmissionStore()
    submission_id = store.save_tool_submission(submission)
    
    # Queue background analysis
    background_tasks.add_task(
        analyze_submitted_tool,
        submission_id,
        str(submission.url),
        submission.name,
    )
    
    # Determine review time
    if submission.is_owner and submission.submitter_email:
        review_time = "24-48 hours (priority)"
    else:
        review_time = "3-5 business days"
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message=f"Thank you for submitting {submission.name}! We'll analyze it and get back to you.",
        estimated_review_time=review_time,
    )


@router.post("/news", response_model=SubmissionResponse)
async def submit_news_tip(submission: NewsSubmission):
    """
    Submit a news tip about AI developments.
    
    We appreciate tips about:
    - Breaking AI news
    - Research papers
    - Industry announcements
    - Tool launches
    """
    store = SubmissionStore()
    submission_id = store.save_news_submission(submission)
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message="Thanks for the tip! Our editorial team will review it.",
        estimated_review_time="1-2 business days",
    )


@router.post("/podcast", response_model=SubmissionResponse)
async def submit_podcast(submission: PodcastSubmission):
    """
    Submit an AI-focused podcast for our directory.
    """
    store = SubmissionStore()
    submission_id = store.save_podcast_submission(submission)
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message=f"Thanks for recommending {submission.name}! We'll review it for inclusion.",
        estimated_review_time="5-7 business days",
    )


@router.get("/status/{submission_id}")
async def get_submission_status(submission_id: str):
    """Check the status of your submission"""
    store = SubmissionStore()
    submission = store.get_submission(submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return {
        "submission_id": submission_id,
        "type": submission["type"],
        "status": submission["status"],
        "submitted_at": submission["submitted_at"],
        "name": submission["data"].get("name") or submission["data"].get("title"),
    }


@router.get("/list")
async def list_submissions(
    submission_type: Optional[str] = None,
    status: Optional[str] = None,
):
    """List submissions (admin only in production)"""
    store = SubmissionStore()
    submissions = store.list_submissions(submission_type, status)
    
    return {
        "count": len(submissions),
        "submissions": [
            {
                "id": s["id"],
                "type": s["type"],
                "status": s["status"],
                "name": s["data"].get("name") or s["data"].get("title"),
                "submitted_at": s["submitted_at"],
            }
            for s in submissions
        ],
    }


# ===========================================
# Background Analysis
# ===========================================

async def analyze_submitted_tool(submission_id: str, url: str, name: str):
    """
    Background task to analyze a submitted tool.
    Creates a draft for review if analysis succeeds.
    """
    logger.info("Analyzing submitted tool", submission_id=submission_id, url=url)
    
    try:
        # Run trust analysis
        trust_engine = TrustEngine()
        analysis = await trust_engine.analyze_tool(url, name)
        
        # Classify vertical
        classifier = VerticalClassifier()
        # We'd need the description here - simplified for now
        vertical = "general"
        
        # Get original submission
        store = SubmissionStore()
        submission = store.get_submission(submission_id)
        
        if not submission:
            return
        
        data = submission["data"]
        
        # Create tool data
        tool = ToolData(
            name=data["name"],
            slug="",
            description=data["description"],
            url=data["url"],
            logo_url=data.get("logo_url"),
            vertical=Vertical(data.get("vertical", "general")) if data.get("vertical") in [v.value for v in Vertical] else Vertical.GENERAL,
            categories=data.get("categories", ["general"]),
            tags=data.get("features", []),
            trust_score=analysis.trust_score,
            wrapper_status=analysis.wrapper_status,
            wrapper_likelihood=analysis.wrapper_likelihood,
            is_verified=False,
            proprietary_tech_score=analysis.proprietary_tech_score,
            reliability_score=analysis.reliability_score,
            transparency_score=analysis.transparency_score,
            liveness_score=analysis.liveness_score,
            signals=analysis.signals,
            detected_technologies=analysis.detected_technologies,
            api_dependencies=analysis.api_dependencies,
            pricing=ToolPricing(
                type=PricingType(data.get("pricing_type", "freemium")),
                starting_price=data.get("pricing_amount"),
                currency="USD",
                billing_period="monthly",
            ),
            source="user_submission",
            source_url=data["url"],
        )
        
        # Save as draft
        draft_store = ContentDraftStore()
        draft_id = f"sub_{submission_id}"
        
        # Calculate quality score
        quality = 0.5
        if analysis.trust_score >= 60:
            quality += 0.2
        if data.get("submitter_email"):
            quality += 0.1
        if data.get("is_owner"):
            quality += 0.1
        if len(data.get("description", "")) >= 100:
            quality += 0.1
        
        draft_store.save_tool_draft(draft_id, tool, min(1.0, quality))
        
        # Update submission status
        store.update_status(
            submission_id,
            "analyzed",
            f"Trust Score: {analysis.trust_score}, Status: {analysis.wrapper_status.value}",
        )
        
        logger.info(
            "Submitted tool analyzed",
            submission_id=submission_id,
            trust_score=analysis.trust_score,
        )
        
    except Exception as e:
        logger.error("Failed to analyze submission", submission_id=submission_id, error=str(e))
        store = SubmissionStore()
        store.update_status(submission_id, "error", str(e))

