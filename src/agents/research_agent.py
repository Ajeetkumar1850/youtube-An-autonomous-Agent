"""
Research Agent - Using Groq API
"""
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.agents.llm_helper import generate_with_cache
from src.cache import cache_manager
from src.config import settings

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def research_topics(niche: str) -> Dict[str, any]:
    """Research trending topics using Groq API"""
    logger.info("research_agent_started", niche=niche)
    
    prompt = f"""Generate 10 trending YouTube video ideas for: {niche}

Requirements:
- Optimized for YouTube Shorts
- Emotionally engaging
- Modern trends
- High click potential

Format: One idea per line."""
    
    try:
        response = await generate_with_cache(
            prompt=prompt,
            cache_key=f"research:{niche}"
        )
        
        topics = [line.strip() for line in response.split("\n") if line.strip()]
        
        logger.info("research_agent_completed", niche=niche, topics_count=len(topics))
        
        return {
            "topics": topics,
            "raw_response": response
        }
        
    except Exception as e:
        logger.error("research_agent_failed", niche=niche, error=str(e))
        raise


def research_agent_node(state: Dict) -> Dict:
    """LangGraph node for research agent"""
    import asyncio
    
    niche = state.get("niche")
    result = asyncio.run(research_topics(niche))
    
    topics = result["topics"]
    selected_topic = topics[0] if topics else None
    
    return {
        **state,
        "topics": topics,
        "selected_topic": selected_topic
    }
