"""
Content Orchestrator Agent

Coordinates the entire content pipeline:
1. Receives content requests (new tools, news sources)
2. Routes to appropriate agents in sequence
3. Manages state and error handling
4. Publishes final approved content
"""
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
from langgraph.graph import StateGraph, END

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.core.redis import redis_client
from app.core.config import settings


class ContentOrchestrator:
    """
    Main orchestrator for the content pipeline.
    Uses LangGraph for stateful workflow management.
    """
    
    def __init__(self):
        self.logger = structlog.get_logger().bind(component="orchestrator")
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        from langgraph.graph import StateGraph
        
        # Define the workflow graph
        workflow = StateGraph(dict)
        
        # Add nodes for each agent
        workflow.add_node("research", self._research_node)
        workflow.add_node("write", self._write_node)
        workflow.add_node("enrich", self._enrich_node)
        workflow.add_node("cite", self._cite_node)
        workflow.add_node("format", self._format_node)
        workflow.add_node("rewrite", self._rewrite_node)
        workflow.add_node("publish", self._publish_node)
        
        # Define edges (workflow sequence)
        workflow.set_entry_point("research")
        workflow.add_edge("research", "write")
        workflow.add_edge("write", "enrich")
        workflow.add_edge("enrich", "cite")
        workflow.add_edge("cite", "format")
        workflow.add_edge("format", "rewrite")
        workflow.add_edge("rewrite", "publish")
        workflow.add_edge("publish", END)
        
        return workflow.compile()
    
    async def _research_node(self, state: dict) -> dict:
        """Research/Scraper agent node"""
        from app.agents.scraper.researcher import ResearcherAgent
        
        agent = ResearcherAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["research_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _write_node(self, state: dict) -> dict:
        """Writer agent node"""
        from app.agents.writer import WriterAgent
        
        agent = WriterAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["write_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _enrich_node(self, state: dict) -> dict:
        """Content enricher agent node"""
        from app.agents.enricher import EnricherAgent
        
        agent = EnricherAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["enrich_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _cite_node(self, state: dict) -> dict:
        """Citation manager agent node"""
        from app.agents.citation import CitationAgent
        
        agent = CitationAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["cite_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _format_node(self, state: dict) -> dict:
        """Formatter agent node"""
        from app.agents.formatter import FormatterAgent
        
        agent = FormatterAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["format_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _rewrite_node(self, state: dict) -> dict:
        """Rewriter agent node"""
        from app.agents.rewriter import RewriterAgent
        
        agent = RewriterAgent()
        context = AgentContext(**state["context"])
        result = await agent.run(context)
        
        state["rewrite_result"] = result.model_dump()
        state["context"] = context.model_dump()
        return state
    
    async def _publish_node(self, state: dict) -> dict:
        """Publisher node - saves draft and auto-publishes high-quality content"""
        from app.services.content import ContentService
        from app.services.publisher import MDXPublisher
        from app.models import ToolData, NewsData
        
        context = AgentContext(**state["context"])
        content_service = ContentService()
        
        # Save as draft first
        draft_id = await content_service.save_draft(context)
        state["draft_id"] = draft_id
        
        # Check for auto-approval based on quality score
        quality_score = context.processed_content.get("quality_score", 0) if context.processed_content else 0
        
        if quality_score >= settings.AUTO_APPROVE_THRESHOLD:
            self.logger.info(
                "Auto-publishing high-quality content",
                draft_id=draft_id,
                quality_score=quality_score,
            )
            
            # Publish to MDX files
            publisher = MDXPublisher()
            
            try:
                if context.content_type == "tool":
                    tool_data = self._build_tool_data(context)
                    file_path = publisher.publish_tool(tool_data)
                    state["published_path"] = file_path
                    state["status"] = "published"
                elif context.content_type == "news":
                    news_data = self._build_news_data(context)
                    file_path = publisher.publish_news(news_data)
                    state["published_path"] = file_path
                    state["status"] = "published"
                    
                # Mark draft as published
                await content_service.mark_as_published(draft_id)
                
            except Exception as e:
                self.logger.error("Auto-publish failed", error=str(e))
                state["status"] = "pending_review"
        else:
            state["status"] = "pending_review"
        
        return state
    
    def _build_tool_data(self, context: AgentContext):
        """Build ToolData from context"""
        from app.models import ToolData, PricingInfo, WrapperStatus, Vertical
        
        processed = context.processed_content or {}
        metadata = context.metadata or {}
        
        return ToolData(
            name=processed.get("title", metadata.get("title", "Unknown Tool")),
            slug=processed.get("slug", ""),
            description=processed.get("description", ""),
            url=context.source_url or "",
            vertical=Vertical(processed.get("vertical", "general")),
            categories=processed.get("categories", ["general"]),
            tags=processed.get("tags", []),
            trust_score=int(processed.get("trust_score", 50)),
            wrapper_status=WrapperStatus(processed.get("wrapper_status", "unknown")),
            is_verified=processed.get("quality_score", 0) >= 0.8,
            pricing=PricingInfo(type="freemium"),
            content=processed.get("content", ""),
            detected_technologies=processed.get("technologies", []),
            api_dependencies=processed.get("api_dependencies", []),
            proprietary_tech_score=int(processed.get("proprietary_score", 50)),
            reliability_score=int(processed.get("reliability_score", 50)),
            transparency_score=int(processed.get("transparency_score", 50)),
            liveness_score=int(processed.get("liveness_score", 50)),
        )
    
    def _build_news_data(self, context: AgentContext):
        """Build NewsData from context"""
        from app.models import NewsData, Vertical
        from datetime import datetime
        
        processed = context.processed_content or {}
        metadata = context.metadata or {}
        
        return NewsData(
            title=processed.get("title", metadata.get("title", "Untitled")),
            slug=processed.get("slug", ""),
            excerpt=processed.get("excerpt", ""),
            content=processed.get("content", ""),
            author=processed.get("author", "aboutai Team"),
            published_at=datetime.utcnow(),
            vertical=Vertical(processed.get("vertical", "general")),
            tags=processed.get("tags", []),
            hype_score=int(processed.get("hype_score", 50)),
            source_url=context.source_url,
            citations=processed.get("citations", []),
            sensationalism_signals=processed.get("sensationalism_signals", []),
            factual_signals=processed.get("factual_signals", []),
        )
    
    # ===========================================
    # Public API Methods
    # ===========================================
    
    async def run_pipeline(
        self,
        content_type: str,
        source_url: str = None,
        source_data: dict = None,
    ) -> str:
        """
        Run the full content pipeline.
        
        Args:
            content_type: "tool" or "news"
            source_url: URL to process (for tools or individual news)
            source_data: Pre-scraped data to process
            
        Returns:
            Pipeline ID for tracking
        """
        pipeline_id = str(uuid.uuid4())
        
        self.logger.info(
            "Starting pipeline",
            pipeline_id=pipeline_id,
            content_type=content_type,
            source_url=source_url,
        )
        
        # Initialize context
        context = AgentContext(
            pipeline_id=pipeline_id,
            content_type=content_type,
            source_url=source_url,
            raw_content=source_data.get("content") if source_data else None,
            metadata=source_data or {},
        )
        
        # Store initial state in Redis
        await self._save_pipeline_state(pipeline_id, {
            "status": "running",
            "stage": "research",
            "progress": 0,
            "context": context.model_dump(),
            "started_at": datetime.utcnow().isoformat(),
        })
        
        # Run the graph
        try:
            initial_state = {"context": context.model_dump()}
            final_state = await self.graph.ainvoke(initial_state)
            
            # Update final state
            await self._save_pipeline_state(pipeline_id, {
                "status": "completed",
                "stage": "done",
                "progress": 100,
                "draft_id": final_state.get("draft_id"),
                "completed_at": datetime.utcnow().isoformat(),
            })
            
        except Exception as e:
            self.logger.error("Pipeline failed", pipeline_id=pipeline_id, error=str(e))
            await self._save_pipeline_state(pipeline_id, {
                "status": "failed",
                "error": str(e),
            })
        
        return pipeline_id
    
    async def queue_tool_analysis(self, url: str, priority: str = "normal") -> str:
        """Queue a tool URL for analysis"""
        task_id = str(uuid.uuid4())
        
        # Store task in Redis
        await redis_client.hset(f"task:{task_id}", mapping={
            "type": "tool_analysis",
            "url": url,
            "priority": priority,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
        })
        
        # Queue the Celery task
        from app.tasks.pipeline_tasks import analyze_tool
        analyze_tool.delay(task_id, url)
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        data = await redis_client.hgetall(f"task:{task_id}")
        return data if data else None
    
    async def _save_pipeline_state(self, pipeline_id: str, state: dict):
        """Save pipeline state to Redis"""
        await redis_client.hset(f"pipeline:{pipeline_id}", mapping={
            k: str(v) if not isinstance(v, str) else v
            for k, v in state.items()
        })
        # Set expiration (24 hours)
        await redis_client.expire(f"pipeline:{pipeline_id}", 86400)
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline status from Redis"""
        data = await redis_client.hgetall(f"pipeline:{pipeline_id}")
        return data if data else None

