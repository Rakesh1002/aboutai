"""
Scraper agents and sources for content discovery.
"""
from .launch_sites import (
    LaunchItem,
    ProductHuntScraper,
    HackerNewsScraper,
    GitHubTrendingScraper,
    AIDirectoryScraper,
    BetaListScraper,
    LaunchSiteAggregator,
)
from .podcasts import (
    PodcastShow,
    PodcastEpisode,
    PodcastFeedParser,
    PodcastAggregator,
    AI_PODCAST_FEEDS,
)
from .browser import browser_pool, scrape_with_browser

__all__ = [
    # Launch Sites
    "LaunchItem",
    "ProductHuntScraper",
    "HackerNewsScraper",
    "GitHubTrendingScraper",
    "AIDirectoryScraper",
    "BetaListScraper",
    "LaunchSiteAggregator",
    # Browser
    "browser_pool",
    "scrape_with_browser",
    # Podcasts
    "PodcastShow",
    "PodcastEpisode",
    "PodcastFeedParser",
    "PodcastAggregator",
    "AI_PODCAST_FEEDS",
]
