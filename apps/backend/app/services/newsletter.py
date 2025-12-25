"""
Newsletter Service with Beehiiv Integration
Handles email signups, digest generation, and newsletter publishing.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import httpx
import structlog
from datetime import datetime, timedelta
import jinja2
import os

logger = structlog.get_logger()


@dataclass
class NewsletterSubscriber:
    email: str
    name: Optional[str] = None
    subscribed_at: datetime = None
    tags: List[str] = None
    
    def __post_init__(self):
        self.subscribed_at = self.subscribed_at or datetime.utcnow()
        self.tags = self.tags or []


@dataclass
class NewsletterContent:
    subject: str
    preview_text: str
    html_content: str
    text_content: str
    send_at: Optional[datetime] = None


class BeehiivClient:
    """
    Client for Beehiiv newsletter API.
    https://developers.beehiiv.com/
    """
    
    def __init__(self, api_key: str = None, publication_id: str = None):
        self.api_key = api_key or os.getenv("BEEHIIV_API_KEY")
        self.publication_id = publication_id or os.getenv("BEEHIIV_PUBLICATION_ID")
        self.base_url = "https://api.beehiiv.com/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def add_subscriber(
        self, 
        email: str, 
        utm_source: str = "aboutai",
        custom_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Add a new subscriber to the newsletter"""
        if not self.api_key:
            logger.warning("Beehiiv API key not configured")
            return {"success": False, "error": "API not configured"}
        
        try:
            payload = {
                "email": email,
                "utm_source": utm_source,
                "reactivate_existing": True,
            }
            
            if custom_fields:
                payload["custom_fields"] = [
                    {"name": k, "value": v} for k, v in custom_fields.items()
                ]
            
            response = await self.client.post(
                f"{self.base_url}/publications/{self.publication_id}/subscriptions",
                headers=self.headers,
                json=payload,
            )
            
            if response.status_code in [200, 201]:
                logger.info("Subscriber added to Beehiiv", email=email)
                return {"success": True, "data": response.json()}
            else:
                logger.warning("Failed to add subscriber", status=response.status_code, response=response.text)
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error("Beehiiv API error", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def create_post(
        self,
        title: str,
        content_html: str,
        subtitle: str = None,
        audience: str = "all",
        status: str = "draft",
    ) -> Dict[str, Any]:
        """Create a new post/newsletter"""
        if not self.api_key:
            logger.warning("Beehiiv API key not configured")
            return {"success": False, "error": "API not configured"}
        
        try:
            payload = {
                "title": title,
                "subtitle": subtitle,
                "content_html": content_html,
                "audience": audience,
                "status": status,
            }
            
            response = await self.client.post(
                f"{self.base_url}/publications/{self.publication_id}/posts",
                headers=self.headers,
                json=payload,
            )
            
            if response.status_code in [200, 201]:
                logger.info("Post created in Beehiiv", title=title)
                return {"success": True, "data": response.json()}
            else:
                logger.warning("Failed to create post", status=response.status_code)
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error("Beehiiv API error", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_subscribers_count(self) -> int:
        """Get total subscriber count"""
        if not self.api_key:
            return 0
        
        try:
            response = await self.client.get(
                f"{self.base_url}/publications/{self.publication_id}",
                headers=self.headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("total_subscribers", 0)
            return 0
            
        except Exception as e:
            logger.error("Failed to get subscriber count", error=str(e))
            return 0


class NewsletterGenerator:
    """
    Generates newsletter content from scraped news and tool data.
    """
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Create default template if not exists
        self._ensure_templates()
        
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def _ensure_templates(self):
        """Ensure default templates exist"""
        weekly_template_path = os.path.join(self.template_dir, "weekly_digest.html")
        if not os.path.exists(weekly_template_path):
            template_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }
        .header p {
            margin: 10px 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .section h2 {
            color: #667eea;
            margin-top: 0;
            font-size: 20px;
            border-bottom: 2px solid #f0f0f5;
            padding-bottom: 10px;
        }
        .tool-card, .news-card {
            border-left: 4px solid #667eea;
            padding: 16px;
            margin: 16px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }
        .tool-card h3, .news-card h3 {
            margin: 0 0 8px;
            font-size: 16px;
        }
        .tool-card a, .news-card a {
            color: #667eea;
            text-decoration: none;
        }
        .tool-card a:hover, .news-card a:hover {
            text-decoration: underline;
        }
        .trust-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }
        .trust-high { background: #d4edda; color: #155724; }
        .trust-medium { background: #fff3cd; color: #856404; }
        .trust-low { background: #f8d7da; color: #721c24; }
        .podcast-item {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f5;
        }
        .podcast-item:last-child {
            border-bottom: none;
        }
        .podcast-artwork {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            margin-right: 16px;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 16px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 14px;
        }
        .footer a {
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 aboutAI Weekly</h1>
        <p>{{ week_range }}</p>
    </div>
    
    {% if featured_tool %}
    <div class="section">
        <h2>⭐ Featured Tool</h2>
        <div class="tool-card">
            <h3>
                <a href="{{ featured_tool.url }}">{{ featured_tool.title }}</a>
                {% if featured_tool.trust_score >= 70 %}
                <span class="trust-badge trust-high">Trust: {{ featured_tool.trust_score }}%</span>
                {% elif featured_tool.trust_score >= 40 %}
                <span class="trust-badge trust-medium">Trust: {{ featured_tool.trust_score }}%</span>
                {% else %}
                <span class="trust-badge trust-low">Trust: {{ featured_tool.trust_score }}%</span>
                {% endif %}
            </h3>
            <p>{{ featured_tool.description[:200] }}...</p>
        </div>
    </div>
    {% endif %}
    
    {% if new_tools %}
    <div class="section">
        <h2>🚀 New AI Tools This Week</h2>
        {% for tool in new_tools[:5] %}
        <div class="tool-card">
            <h3><a href="{{ tool.url }}">{{ tool.title }}</a></h3>
            <p style="margin: 0; color: #6c757d; font-size: 14px;">{{ tool.category }} • {{ tool.pricing }}</p>
        </div>
        {% endfor %}
        <a href="https://aboutai.app/tools" class="cta-button">View All Tools →</a>
    </div>
    {% endif %}
    
    {% if top_news %}
    <div class="section">
        <h2>📰 Top AI News</h2>
        {% for news in top_news[:5] %}
        <div class="news-card">
            <h3><a href="{{ news.url }}">{{ news.title }}</a></h3>
            <p style="margin: 4px 0 0; color: #6c757d; font-size: 13px;">{{ news.source }} • {{ news.published_at }}</p>
        </div>
        {% endfor %}
        <a href="https://aboutai.app/news" class="cta-button">Read All News →</a>
    </div>
    {% endif %}
    
    {% if podcast_episodes %}
    <div class="section">
        <h2>🎙️ Podcast Picks</h2>
        {% for episode in podcast_episodes[:3] %}
        <div class="podcast-item">
            <div>
                <strong>{{ episode.show_title }}</strong><br>
                <a href="{{ episode.episode_url }}">{{ episode.title[:60] }}{% if episode.title|length > 60 %}...{% endif %}</a>
            </div>
        </div>
        {% endfor %}
        <a href="https://aboutai.app/podcasts" class="cta-button">All Podcasts →</a>
    </div>
    {% endif %}
    
    <div class="footer">
        <p>
            You're receiving this because you subscribed to aboutAI Weekly.<br>
            <a href="{{ unsubscribe_url }}">Unsubscribe</a> | <a href="https://aboutai.app">Visit aboutai.app</a>
        </p>
        <p style="margin-top: 16px;">
            Made with ❤️ by the aboutAI team
        </p>
    </div>
</body>
</html>'''
            with open(weekly_template_path, 'w') as f:
                f.write(template_content)
    
    def generate_weekly_digest(
        self,
        new_tools: List[Dict[str, Any]],
        top_news: List[Dict[str, Any]],
        podcast_episodes: List[Dict[str, Any]] = None,
        featured_tool: Dict[str, Any] = None,
    ) -> NewsletterContent:
        """Generate weekly digest newsletter"""
        
        # Calculate week range
        today = datetime.now()
        week_start = today - timedelta(days=7)
        week_range = f"{week_start.strftime('%b %d')} - {today.strftime('%b %d, %Y')}"
        
        # Render HTML
        template = self.env.get_template("weekly_digest.html")
        html_content = template.render(
            subject="This Week in AI",
            week_range=week_range,
            new_tools=new_tools,
            top_news=top_news,
            podcast_episodes=podcast_episodes or [],
            featured_tool=featured_tool,
            unsubscribe_url="{{unsubscribe_url}}",  # Beehiiv will replace this
        )
        
        # Generate plain text version
        text_content = self._generate_plain_text(
            new_tools, top_news, podcast_episodes, week_range
        )
        
        return NewsletterContent(
            subject=f"🤖 This Week in AI: {len(new_tools)} New Tools & Top News",
            preview_text=f"Discover {len(new_tools)} new AI tools and catch up on the latest AI news.",
            html_content=html_content,
            text_content=text_content,
        )
    
    def _generate_plain_text(
        self,
        new_tools: List[Dict[str, Any]],
        top_news: List[Dict[str, Any]],
        podcast_episodes: List[Dict[str, Any]],
        week_range: str,
    ) -> str:
        """Generate plain text version of newsletter"""
        lines = [
            "aboutAI Weekly",
            week_range,
            "=" * 50,
            "",
            "NEW AI TOOLS THIS WEEK",
            "-" * 30,
        ]
        
        for tool in new_tools[:5]:
            lines.append(f"• {tool.get('title', 'Unknown')}")
            lines.append(f"  {tool.get('url', '')}")
            lines.append("")
        
        lines.extend([
            "",
            "TOP AI NEWS",
            "-" * 30,
        ])
        
        for news in top_news[:5]:
            lines.append(f"• {news.get('title', 'Unknown')}")
            lines.append(f"  {news.get('url', '')}")
            lines.append("")
        
        if podcast_episodes:
            lines.extend([
                "",
                "PODCAST PICKS",
                "-" * 30,
            ])
            for ep in podcast_episodes[:3]:
                lines.append(f"• {ep.get('show_title', '')}: {ep.get('title', '')}")
                lines.append("")
        
        lines.extend([
            "",
            "=" * 50,
            "Visit aboutai.app for more",
            "",
        ])
        
        return "\n".join(lines)


class NewsletterService:
    """
    Main newsletter service that combines generation and sending.
    """
    
    def __init__(self):
        self.beehiiv = BeehiivClient()
        self.generator = NewsletterGenerator()
    
    async def subscribe(self, email: str, source: str = "website") -> Dict[str, Any]:
        """Subscribe a new user to the newsletter"""
        logger.info("Processing newsletter subscription", email=email)
        
        # Add to Beehiiv
        result = await self.beehiiv.add_subscriber(email, utm_source=source)
        
        if result.get("success"):
            logger.info("Subscription successful", email=email)
        else:
            logger.warning("Subscription failed", email=email, error=result.get("error"))
        
        return result
    
    async def create_weekly_digest(
        self,
        new_tools: List[Dict[str, Any]],
        top_news: List[Dict[str, Any]],
        podcast_episodes: List[Dict[str, Any]] = None,
        publish: bool = False,
    ) -> Dict[str, Any]:
        """Create and optionally publish weekly digest"""
        
        # Select featured tool (highest trust score or most recent)
        featured_tool = None
        if new_tools:
            sorted_tools = sorted(
                new_tools,
                key=lambda x: x.get("trust_score", 0),
                reverse=True
            )
            featured_tool = sorted_tools[0] if sorted_tools else None
        
        # Generate content
        content = self.generator.generate_weekly_digest(
            new_tools=new_tools,
            top_news=top_news,
            podcast_episodes=podcast_episodes,
            featured_tool=featured_tool,
        )
        
        if publish:
            # Create as draft in Beehiiv
            result = await self.beehiiv.create_post(
                title=content.subject,
                subtitle=content.preview_text,
                content_html=content.html_content,
                status="draft",  # Manual review before sending
            )
            return {
                "content": content,
                "beehiiv_result": result,
            }
        
        return {"content": content}
    
    async def get_subscriber_count(self) -> int:
        """Get total newsletter subscribers"""
        return await self.beehiiv.get_subscribers_count()
