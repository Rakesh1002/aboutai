"""
Celery application configuration for aboutai backend.
Handles background tasks and scheduled jobs.
"""
import ssl
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from app.core.config import settings


# Get Redis URL (supports Upstash)
broker_url = settings.celery_broker_url

# Create Celery app
celery_app = Celery(
    "aboutai",
    broker=broker_url,
    backend=broker_url,
    include=[
        "app.tasks.pipeline_tasks",
        "app.tasks.scraper_tasks",
    ],
)

# SSL settings for Upstash (rediss://)
if broker_url.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE
    }
    celery_app.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE
    }

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Results
    result_expires=86400,  # 24 hours
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Beat scheduler
    beat_schedule={
        # ===========================================
        # Content Pipeline
        # ===========================================
        "run-full-pipeline-every-4-hours": {
            "task": "pipeline.start_full_content_pipeline",
            "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours
            "options": {"queue": "pipeline"},
        },
        
        # ===========================================
        # Launch Site Scrapers
        # ===========================================
        "scrape-launch-sites-every-6-hours": {
            "task": "pipeline.scrape_launch_sites",
            "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
            "options": {"queue": "scraper"},
        },
        
        # ===========================================
        # Podcast Directory
        # ===========================================
        "update-podcast-directory-daily": {
            "task": "pipeline.update_podcast_directory",
            "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
            "options": {"queue": "scraper"},
        },
        
        # ===========================================
        # Newsletter
        # ===========================================
        "generate-weekly-newsletter": {
            "task": "pipeline.generate_weekly_newsletter",
            "schedule": crontab(minute=0, hour=10, day_of_week=1),  # Mondays at 10 AM
            "options": {"queue": "publisher"},
        },
    },
    
    # Task routing
    task_routes={
        "pipeline.*": {"queue": "pipeline"},
        "scraper.*": {"queue": "scraper"},
        "publisher.*": {"queue": "publisher"},
    },
    
    # Default queue
    task_default_queue="default",
)


def get_celery_app():
    """Get the Celery app instance"""
    return celery_app
