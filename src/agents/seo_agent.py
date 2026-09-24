"""
SEO Agent - Upgraded with structured output and caching
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.cache import cache_manager
from src.config import settings

logger = structlog.get_logger()


class SEOMetadata(BaseModel):
    """Structured SEO metadata"""
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]


def parse_seo_response(content: str) -> SEOMetadata:
    """Parse LLM response into structured SEO metadata"""
    title = ""
    description = ""
    tags = []
    hashtags = []
    
    lines = content.split("\n")
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.upper().startswith("TITLE:"):
            current_section = "title"
            title = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.upper().startswith("DESCRIPTION:"):
            current_section = "description"
            description = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.upper().startswith("HASHTAGS:"):
            current_section = "hashtags"
            hashtag_text = line.split(":", 1)[1].strip() if ":" in line else ""
            if hashtag_text:
                hashtags = [h.strip() for h in hashtag_text.split() if h.startswith("#")]
        elif line.upper().startswith("TAGS:"):
            current_section = "tags"
            tag_text = line.split(":", 1)[1].strip() if ":" in line else ""
            if tag_text:
                tags = [t.strip() for t in tag_text.split(",") if t.strip()]
        elif current_section and line:
            # Continue previous section
            if current_section == "title" and not title:
                title = line
            elif current_section == "description" and not description:
                description = line
    
    # Fallbacks
    if not title:
        title = "AI Generated Video"
    if not description:
        description = "Created with autonomous AI agents"
    if not tags:
        tags = ["AI", "automated", "content"]
    if not hashtags:
        hashtags = ["#AI", "#content", "#video"]
    
    return SEOMetadata(
        title=title[:100],  # YouTube title limit
        description=description[:500],  # Keep description concise
        tags=tags[:10],  # Max 10 tags
        hashtags=hashtags[:10]
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_seo(topic: str, script: str) -> SEOMetadata:
    """
    Generate SEO metadata for YouTube video
    """
    logger.info("seo_agent_started", topic=topic)
    
    # Check cache
    cache_key = f"seo:{topic}"
    cached_response = await cache_manager.get_llm_response(
        model=settings.ollama_model,
        prompt=cache_key
    )
    
    if cached_response:
        logger.info("seo_agent_cache_hit")
        return parse_seo_response(cached_response)
    
    prompt = f"""
    You are a professional YouTube SEO expert.

    Generate SEO metadata for this YouTube Shorts video.

    Topic:
    {topic}

    Script Preview:
    {script[:300]}...

    STRICT FORMAT:

    TITLE:
    (one viral clickable title only, max 100 characters)

    DESCRIPTION:
    (2 short engaging lines)

    HASHTAGS:
    (10 hashtags in one line, each starting with #)

    TAGS:
    (10 comma-separated SEO tags)

    Rules:
    - No explanations
    - No extra text
    - No markdown
    - No numbering
    - Keep title short and viral
    - Make it clickable and engaging
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
        
        # Cache for 24 hours
        await cache_manager.set_llm_response(
            model=settings.ollama_model,
            prompt=cache_key,
            response=content,
            ttl=86400
        )
        
        seo_data = parse_seo_response(content)
        
        logger.info(
            "seo_agent_completed",
            title=seo_data.title,
            tags_count=len(seo_data.tags),
            hashtags_count=len(seo_data.hashtags)
        )
        
        await cache_manager.increment_metric("seo_agent_calls")
        
        return seo_data
        
    except Exception as e:
        logger.error("seo_agent_failed", error=str(e))
        raise


def seo_agent_node(state: Dict) -> Dict:
    """LangGraph node for SEO agent"""
    import asyncio
    
    topic = state.get("selected_topic")
    script = state.get("script")
    
    if not topic or not script:
        raise ValueError("Topic and script required for SEO generation")
    
    seo_data = asyncio.run(generate_seo(topic, script))
    
    return {
        **state,
        "seo_title": seo_data.title,
        "seo_description": seo_data.description,
        "seo_tags": seo_data.tags,
        "seo_hashtags": seo_data.hashtags
    }
