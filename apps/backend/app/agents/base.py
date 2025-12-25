"""
Base Agent class for all pipeline agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import structlog
from pydantic import BaseModel

from app.core.config import settings


class AgentContext(BaseModel):
    """Context passed between agents in the pipeline"""
    pipeline_id: str
    content_type: str  # "tool" or "news"
    source_url: Optional[str] = None
    raw_content: Optional[str] = None
    processed_content: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    citations: list = []
    errors: list = []
    started_at: datetime = datetime.utcnow()
    
    def add_error(self, agent: str, error: str):
        self.errors.append({
            "agent": agent,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def add_citation(self, url: str, title: str, source: str, snippet: str = None):
        self.citations.append({
            "url": url,
            "title": title,
            "source": source,
            "snippet": snippet,
            "accessed_at": datetime.utcnow().isoformat(),
        })


class AgentResult(BaseModel):
    """Result from an agent's processing"""
    success: bool
    agent_name: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0
    tokens_used: int = 0


class BaseAgent(ABC):
    """Base class for all pipeline agents"""
    
    name: str = "base_agent"
    version: str = "1.0.0"
    
    def __init__(self):
        self.logger = structlog.get_logger().bind(agent=self.name)
    
    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResult:
        """Process the context and return a result"""
        pass
    
    async def run(self, context: AgentContext) -> AgentResult:
        """Run the agent with timing and error handling"""
        import time
        start_time = time.time()
        
        self.logger.info("Agent started", pipeline_id=context.pipeline_id)
        
        try:
            result = await self.process(context)
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            self.logger.info(
                "Agent completed",
                pipeline_id=context.pipeline_id,
                success=result.success,
                processing_time_ms=result.processing_time_ms,
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                "Agent failed",
                pipeline_id=context.pipeline_id,
                error=error_msg,
            )
            context.add_error(self.name, error_msg)
            
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=error_msg,
                processing_time_ms=(time.time() - start_time) * 1000,
            )
    
    def get_llm_client(self, provider: str = None, model: str = None):
        """Get LLM client based on configuration"""
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        model = model or settings.DEFAULT_LLM_MODEL
        
        if provider == "openai":
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=settings.OPENAI_API_KEY), model
        elif provider == "anthropic":
            from anthropic import AsyncAnthropic
            return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY), model
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

