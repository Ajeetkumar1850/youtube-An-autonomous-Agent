"""
Script Agent - Using Groq API
"""
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.agents.llm_helper import generate_with_cache

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_script(topic: str) -> str:
    """Generate Hindi storytelling script"""
    logger.info("script_agent_started", topic=topic)
    
    prompt = f"""Write a 45-60 second Hindi storytelling script for YouTube Shorts about: {topic}

Requirements:
- Write ONLY in Hindi (Devanagari script)
- Conversational tone for kids
- Emotional and dramatic
- Add curiosity and suspense
- Simple Hindi words
- NO markdown, NO numbering, NO English
- 45-60 seconds when spoken

Write the script directly:"""
    
    try:
        script = await generate_with_cache(
            prompt=prompt,
            cache_key=f"script:{topic}"
        )
        
        logger.info("script_agent_completed", script_length=len(script))
        return script.strip()
        
    except Exception as e:
        logger.error("script_agent_failed", error=str(e))
        raise


def script_agent_node(state: Dict) -> Dict:
    """LangGraph node"""
    import asyncio
    
    topic = state.get("selected_topic") or state.get("niche")
    script = asyncio.run(generate_script(topic))
    
    return {
        **state,
        "script": script
    }
