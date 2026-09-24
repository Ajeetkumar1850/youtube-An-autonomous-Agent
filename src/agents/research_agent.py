"""
Research Agent - Upgraded with caching and error handling
"""
from typing import Dict
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.cache import cache_manager
from src.config import settings

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def research_topics(niche: str) -> Dict[str, any]:
    """
    Research trending topics in the given niche
    Uses caching to avoid redundant LLM calls
    """
    logger.info("research_agent_started", niche=niche)
    
    # Check cache first
    cached_response = await cache_manager.get_llm_response(
        model=settings.ollama_model,
        prompt=f"research:{niche}"
    )
    
    if cached_response:
        logger.info("research_agent_cache_hit", niche=niche)
        return {
            "topics": cached_response.split("\n"),
            "raw_response": cached_response
        }
    
    prompt = f"""
    You are a professional YouTube strategist.
    Generate 10 high-CTR YouTube video ideas for the niche: {niche}

    Requirements:
    - Optimized for shorts
    - Emotionally engaging
    - Modern trends
    - High click potential
    - Beginner audience

    Also include:
    - Estimated virality score out of 10
    
    Format each topic on a new line.
    """
    
    try:
        response = ollama.chat(
            model=settings.ollama_model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        content = response['message']['content'].strip()
        
        # Cache the response for 24 hours
        await cache_manager.set_llm_response(
            model=settings.ollama_model,
            prompt=f"research:{niche}",
            response=content,
            ttl=86400
        )
        
        topics = [line.strip() for line in content.split("\n") if line.strip()]
        
        logger.info(
            "research_agent_completed",
            niche=niche,
            topics_count=len(topics)
        )
        
        await cache_manager.increment_metric("research_agent_calls")
        
        return {
            "topics": topics,
            "raw_response": content
        }
        
    except Exception as e:
        logger.error("research_agent_failed", niche=niche, error=str(e))
        raise


def research_agent_node(state: Dict) -> Dict:
    """LangGraph node for research agent"""
    import asyncio
    
    niche = state.get("niche")
    
    # Run async function in sync context
    result = asyncio.run(research_topics(niche))
    
    topics = result["topics"]
    selected_topic = topics[0] if topics else None
    
    return {
        **state,
        "topics": topics,
        "selected_topic": selected_topic
    }
