"""
Script Agent - Upgraded with caching and retry logic
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
async def generate_script(topic: str) -> str:
    """
    Generate Hindi storytelling script for the topic
    """
    logger.info("script_agent_started", topic=topic)
    
    # Check cache
    cached_response = await cache_manager.get_llm_response(
        model=settings.ollama_model,
        prompt=f"script:{topic}"
    )
    
    if cached_response:
        logger.info("script_agent_cache_hit", topic=topic)
        return cached_response
    
    prompt = f"""
    You are a professional Hindi YouTube Shorts storyteller.

    Create a SHORT emotional storytelling script in Hindi.

    Topic:
    {topic}

    IMPORTANT RULES:
    - Write ONLY in Hindi
    - Make it sound like a real storyteller
    - Conversational tone
    - Emotional narration
    - Cartoon storytelling style
    - Simple Hindi words
    - Add curiosity
    - Add drama
    - Add emotions
    - Add natural pauses

    VERY IMPORTANT:
    - No numbering
    - No bullet points
    - No headings
    - No markdown
    - No labels like Hook/CTA
    - No English
    - No emojis

    The script should feel like:
    - Animated story narration
    - Kids storytelling
    - Cartoon YouTube Shorts

    Keep script around 45–60 seconds.
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
        
        script = response['message']['content'].strip()
        
        # Validate script length (should be reasonable)
        word_count = len(script.split())
        if word_count < 50:
            logger.warning(
                "script_too_short",
                topic=topic,
                word_count=word_count
            )
        
        # Cache for 24 hours
        await cache_manager.set_llm_response(
            model=settings.ollama_model,
            prompt=f"script:{topic}",
            response=script,
            ttl=86400
        )
        
        logger.info(
            "script_agent_completed",
            topic=topic,
            word_count=word_count,
            char_count=len(script)
        )
        
        await cache_manager.increment_metric("script_agent_calls")
        
        return script
        
    except Exception as e:
        logger.error("script_agent_failed", topic=topic, error=str(e))
        raise


def script_agent_node(state: Dict) -> Dict:
    """LangGraph node for script agent"""
    import asyncio
    
    topic = state.get("selected_topic")
    
    if not topic:
        raise ValueError("No topic selected for script generation")
    
    script = asyncio.run(generate_script(topic))
    
    return {
        **state,
        "script": script
    }
