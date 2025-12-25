"""
Celery tasks for web scraping operations.
"""
from celery import shared_task
import structlog

from app.core.celery_app import celery_app

logger = structlog.get_logger()


# Task definitions are in pipeline_tasks.py
# This file is kept for backwards compatibility with celery includes
