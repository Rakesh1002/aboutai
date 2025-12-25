"""
AI Podcast Aggregator
Aggregates and indexes AI-related podcasts and episodes from various sources.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import httpx
import feedparser
from datetime import datetime
import structlog
import asyncio
import re
from bs4 import BeautifulSoup

logger = structlog.get_logger()


@dataclass
class PodcastShow:
    """Represents a podcast show"""
    id: str
    title: str
    description: str
    feed_url: str
    website_url: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    episode_count: int = 0
    latest_episode_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description[:500],
            "feed_url": self.feed_url,
            "website_url": self.website_url,
            "author": self.author,
            "image_url": self.image_url,
            "categories": self.categories,
            "episode_count": self.episode_count,
            "latest_episode_date": self.latest_episode_date.isoformat() if self.latest_episode_date else None,
        }


@dataclass
class PodcastEpisode:
    """Represents a podcast episode"""
    id: str
    show_id: str
    show_title: str
    title: str
    description: str
    audio_url: str
    published_at: datetime
    duration_seconds: Optional[int] = None
    episode_url: Optional[str] = None
    image_url: Optional[str] = None
    guest_names: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "show_id": self.show_id,
            "show_title": self.show_title,
            "title": self.title,
            "description": self.description[:1000],
            "audio_url": self.audio_url,
            "published_at": self.published_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "episode_url": self.episode_url,
            "image_url": self.image_url,
            "guest_names": self.guest_names,
            "topics": self.topics,
        }


# Curated list of AI-focused podcasts with RSS feeds
AI_PODCAST_FEEDS = [
    # AI-Focused Shows
    {
        "title": "Practical AI",
        "feed": "https://changelog.com/practicalai/feed",
        "categories": ["ai", "ml", "production"],
    },
    {
        "title": "The TWIML AI Podcast",
        "feed": "https://feeds.megaphone.fm/MLN2155636147",
        "categories": ["ai", "ml", "research"],
    },
    {
        "title": "Lex Fridman Podcast",
        "feed": "https://lexfridman.com/feed/podcast/",
        "categories": ["ai", "tech", "interviews"],
    },
    {
        "title": "Machine Learning Street Talk",
        "feed": "https://anchor.fm/s/1e4a0eac/podcast/rss",
        "categories": ["ml", "research", "technical"],
    },
    {
        "title": "The AI Alignment Podcast",
        "feed": "https://futureoflife.org/feed/the-future-of-life-podcast/",
        "categories": ["ai safety", "alignment", "research"],
    },
    {
        "title": "Gradient Dissent",
        "feed": "https://feeds.soundcloud.com/users/soundcloud:users:774544815/sounds.rss",
        "categories": ["ml", "interviews", "industry"],
    },
    {
        "title": "Data Skeptic",
        "feed": "https://dataskeptic.libsyn.com/rss",
        "categories": ["data science", "ml", "education"],
    },
    {
        "title": "Talking Machines",
        "feed": "https://www.thetalkingmachines.com/feed",
        "categories": ["ml", "research", "interviews"],
    },
    {
        "title": "The AI Podcast (NVIDIA)",
        "feed": "https://feeds.soundcloud.com/users/soundcloud:users:264034133/sounds.rss",
        "categories": ["ai", "industry", "nvidia"],
    },
    {
        "title": "No Priors",
        "feed": "https://feeds.megaphone.fm/nopriors",
        "categories": ["ai", "startups", "vc"],
    },
    {
        "title": "Cognitive Revolution",
        "feed": "https://feeds.transistor.fm/the-cognitive-revolution",
        "categories": ["ai", "industry", "interviews"],
    },
    {
        "title": "Last Week in AI",
        "feed": "https://feeds.buzzsprout.com/2025445.rss",
        "categories": ["ai news", "weekly"],
    },
    {
        "title": "AI Engineering",
        "feed": "https://feeds.transistor.fm/latent-space",
        "categories": ["ai engineering", "llm", "technical"],
    },
    {
        "title": "Eye on AI",
        "feed": "https://feeds.megaphone.fm/eye-on-ai",
        "categories": ["ai news", "industry"],
    },
    {
        "title": "Robot Brains",
        "feed": "https://anchor.fm/s/56c1e1ec/podcast/rss",
        "categories": ["robotics", "ai", "interviews"],
    },
]


class PodcastFeedParser:
    """Parses podcast RSS feeds"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def parse_feed(self, feed_url: str, categories: List[str] = None) -> Optional[PodcastShow]:
        """Parse a podcast RSS feed and return show info with episodes"""
        try:
            response = await self.client.get(feed_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            if not feed.feed or not hasattr(feed.feed, 'title'):
                logger.warning("Invalid feed", url=feed_url)
                return None
            
            # Generate show ID from title
            show_id = self._generate_id(feed.feed.get('title', 'unknown'))
            
            # Parse show metadata
            image_url = None
            if hasattr(feed.feed, 'image') and feed.feed.image:
                image_url = feed.feed.image.get('href')
            elif hasattr(feed.feed, 'itunes_image'):
                image_url = feed.feed.itunes_image
            
            latest_date = None
            if feed.entries:
                for entry in feed.entries:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        dt = datetime(*entry.published_parsed[:6])
                        if latest_date is None or dt > latest_date:
                            latest_date = dt
            
            show = PodcastShow(
                id=show_id,
                title=feed.feed.get('title', ''),
                description=feed.feed.get('description', feed.feed.get('summary', '')),
                feed_url=feed_url,
                website_url=feed.feed.get('link'),
                author=feed.feed.get('author', feed.feed.get('itunes_author', '')),
                image_url=image_url,
                categories=categories or [],
                episode_count=len(feed.entries),
                latest_episode_date=latest_date,
            )
            
            return show
            
        except Exception as e:
            logger.error("Failed to parse feed", url=feed_url, error=str(e))
            return None
    
    async def get_recent_episodes(
        self, 
        feed_url: str, 
        show_id: str, 
        show_title: str,
        limit: int = 10
    ) -> List[PodcastEpisode]:
        """Get recent episodes from a feed"""
        try:
            response = await self.client.get(feed_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            episodes = []
            
            for entry in feed.entries[:limit]:
                try:
                    episode = self._parse_episode(entry, show_id, show_title)
                    if episode:
                        episodes.append(episode)
                except Exception as e:
                    logger.warning("Failed to parse episode", error=str(e))
                    continue
            
            return episodes
            
        except Exception as e:
            logger.error("Failed to get episodes", url=feed_url, error=str(e))
            return []
    
    def _parse_episode(self, entry, show_id: str, show_title: str) -> Optional[PodcastEpisode]:
        """Parse a feed entry into a PodcastEpisode"""
        # Get audio URL
        audio_url = None
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if 'audio' in enc.get('type', ''):
                    audio_url = enc.get('href') or enc.get('url')
                    break
        
        if not audio_url:
            return None
        
        # Parse published date
        published_at = datetime.now()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6])
        
        # Get duration
        duration = None
        if hasattr(entry, 'itunes_duration'):
            duration = self._parse_duration(entry.itunes_duration)
        
        # Generate episode ID
        episode_id = self._generate_id(f"{show_id}-{entry.get('title', '')}-{published_at.isoformat()}")
        
        # Extract guest names from title (common pattern: "Episode X: Guest Name on Topic")
        guests = self._extract_guests(entry.get('title', ''), entry.get('summary', ''))
        
        # Extract topics
        topics = self._extract_topics(entry.get('title', ''), entry.get('summary', ''))
        
        return PodcastEpisode(
            id=episode_id,
            show_id=show_id,
            show_title=show_title,
            title=entry.get('title', ''),
            description=entry.get('summary', entry.get('description', '')),
            audio_url=audio_url,
            published_at=published_at,
            duration_seconds=duration,
            episode_url=entry.get('link'),
            guest_names=guests,
            topics=topics,
        )
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds"""
        if not duration_str:
            return None
        
        try:
            # Try numeric (seconds)
            return int(duration_str)
        except:
            pass
        
        # Try HH:MM:SS or MM:SS format
        parts = str(duration_str).split(':')
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except:
            pass
        
        return None
    
    def _extract_guests(self, title: str, description: str) -> List[str]:
        """Extract guest names from title/description"""
        guests = []
        
        # Common patterns
        patterns = [
            r'with\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'featuring\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'guest:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'\|\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        text = f"{title} {description}"
        for pattern in patterns:
            matches = re.findall(pattern, text)
            guests.extend(matches)
        
        return list(set(guests))[:5]  # Limit to 5 unique guests
    
    def _extract_topics(self, title: str, description: str) -> List[str]:
        """Extract AI-related topics from title/description"""
        text = f"{title} {description}".lower()
        
        topic_keywords = [
            "llm", "gpt", "claude", "gemini", "transformer", "diffusion",
            "rag", "fine-tuning", "prompt engineering", "agents", "embeddings",
            "computer vision", "nlp", "speech", "robotics", "autonomous",
            "safety", "alignment", "interpretability", "bias", "ethics",
            "openai", "anthropic", "google ai", "meta ai", "nvidia",
            "hugging face", "langchain", "pytorch", "tensorflow",
        ]
        
        found_topics = []
        for keyword in topic_keywords:
            if keyword in text:
                found_topics.append(keyword)
        
        return found_topics[:10]
    
    def _generate_id(self, text: str) -> str:
        """Generate a URL-safe ID from text"""
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
        return slug.strip('-')[:100]


class PodcastAggregator:
    """
    Aggregates podcasts from multiple sources.
    """
    
    def __init__(self):
        self.parser = PodcastFeedParser()
    
    async def get_all_shows(self) -> List[PodcastShow]:
        """Get all AI podcast shows from curated list"""
        logger.info("Aggregating AI podcast shows")
        
        tasks = [
            self.parser.parse_feed(podcast["feed"], podcast.get("categories", []))
            for podcast in AI_PODCAST_FEEDS
        ]
        
        results = await asyncio.gather(*tasks)
        shows = [r for r in results if r is not None]
        
        # Sort by latest episode date
        shows.sort(
            key=lambda x: x.latest_episode_date or datetime.min,
            reverse=True
        )
        
        logger.info("Found podcast shows", count=len(shows))
        return shows
    
    async def get_recent_episodes(self, limit: int = 50) -> List[PodcastEpisode]:
        """Get recent episodes from all shows"""
        logger.info("Fetching recent podcast episodes")
        
        all_episodes = []
        
        for podcast in AI_PODCAST_FEEDS:
            show_id = self.parser._generate_id(podcast["title"])
            episodes = await self.parser.get_recent_episodes(
                podcast["feed"],
                show_id,
                podcast["title"],
                limit=5
            )
            all_episodes.extend(episodes)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Sort by publication date
        all_episodes.sort(key=lambda x: x.published_at, reverse=True)
        
        logger.info("Found recent episodes", count=len(all_episodes))
        return all_episodes[:limit]
    
    async def discover_new_podcasts(self, query: str = "artificial intelligence") -> List[Dict[str, Any]]:
        """
        Discover new AI podcasts using iTunes Search API.
        """
        logger.info("Discovering new podcasts", query=query)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://itunes.apple.com/search",
                    params={
                        "term": query,
                        "media": "podcast",
                        "limit": 50,
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                podcasts = []
                for result in data.get("results", []):
                    # Filter for AI-related content
                    title = result.get("collectionName", "").lower()
                    genres = [g.lower() for g in result.get("genres", [])]
                    
                    ai_keywords = ["ai", "artificial intelligence", "machine learning", "deep learning", "tech"]
                    if any(kw in title or any(kw in g for g in genres) for kw in ai_keywords):
                        podcasts.append({
                            "title": result.get("collectionName"),
                            "author": result.get("artistName"),
                            "feed_url": result.get("feedUrl"),
                            "artwork_url": result.get("artworkUrl600"),
                            "genres": result.get("genres", []),
                            "track_count": result.get("trackCount", 0),
                        })
                
                logger.info("Discovered podcasts", count=len(podcasts))
                return podcasts
                
        except Exception as e:
            logger.error("Podcast discovery failed", error=str(e))
            return []

