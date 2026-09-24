"""
Shot Agent - Upgraded with validation and retry logic
"""
import re
from typing import Dict, List
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
async def generate_shots(script: str, num_shots: int = 12) -> List[str]:
    """
    Generate cinematic shot descriptions with character actions
    """
    logger.info("shot_agent_started", num_shots=num_shots)
    
    # Check cache
    cache_key = f"shots:{script[:100]}"
    cached_response = await cache_manager.get_llm_response(
        model=settings.ollama_model,
        prompt=cache_key
    )
    
    if cached_response:
        logger.info("shot_agent_cache_hit")
        return _parse_shots(cached_response, num_shots)
    
    prompt = f"""
    You are a professional animated movie storyboard artist.

    Read the Hindi story carefully.

    Generate EXACTLY {num_shots} cinematic animated shot prompts with CHARACTER ACTIONS.

    IMPORTANT RULES:
    - Describe character movements and expressions
    - Include: mouth movements, hand gestures, eye expressions, body language
    - Cartoon animation style
    - Disney Pixar style
    - Cute expressive characters
    - Emotional storytelling visuals
    - Action-focused descriptions
    - Keep shots simple
    - Short prompts only
    - No numbering
    - No explanations
    - No markdown

    GOOD EXAMPLES:

    cartoon mother talking with mouth open, hands gesturing emotionally, tears in eyes
    little boy walking with arms swinging, looking around curiously, expressive face
    mother hugging child tightly, eyes closed, gentle smile, warm expression
    cartoon family walking together, waving hands, laughing with open mouths
    sad child sitting with head down, wiping tears, shoulders slumped
    happy character jumping with arms raised, big smile, excited eyes
    character speaking with animated mouth movements, pointing finger, surprised expression

    Script:
    {script}
    
    Generate {num_shots} shots, one per line.
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
        
        shots = _parse_shots(content, num_shots)
        
        logger.info(
            "shot_agent_completed",
            shots_generated=len(shots),
            required=num_shots
        )
        
        await cache_manager.increment_metric("shot_agent_calls")
        
        return shots
        
    except Exception as e:
        logger.error("shot_agent_failed", error=str(e))
        raise


def _parse_shots(content: str, target_count: int) -> List[str]:
    """Parse and enhance shot descriptions"""
    lines = content.split("\n")
    styled_shots = []
    
    for line in lines:
        line = line.strip()
        
        # Remove numbering
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        line = re.sub(r'^\*\*?\s*', '', line)
        line = re.sub(r'\*\*?\s*$', '', line)
        line = line.strip()
        
        if line and len(line) > 10:
            # Add animation styling
            enhanced = f"{line}, animated character with movement, disney pixar style, expressive animation, colorful lighting, ultra detailed, smooth motion"
            styled_shots.append(enhanced)
    
    # Ensure minimum shots with fallbacks
    default_shots = [
        "cartoon character talking with mouth open, hands gesturing emotionally",
        "character walking with arms swinging, happy expression, eyes blinking",
        "character with surprised face, eyes wide open, hands raised dramatically",
        "character smiling warmly, eyes closed peacefully, gentle expression",
        "character jumping excitedly, arms in air, big smile, dynamic pose",
        "character sitting thoughtfully, hand on chin, contemplative look",
        "character running energetically, arms pumping, determined face",
        "character waving goodbye, sad eyes, emotional moment"
    ]
    
    while len(styled_shots) < target_count:
        default_shot = default_shots[len(styled_shots) % len(default_shots)]
        enhanced = f"{default_shot}, animated character with movement, disney pixar style, expressive animation, colorful lighting, ultra detailed, smooth motion"
        styled_shots.append(enhanced)
        logger.warning(
            "shot_agent_fallback_used",
            current_count=len(styled_shots),
            target=target_count
        )
    
    return styled_shots[:target_count]


def shot_agent_node(state: Dict) -> Dict:
    """LangGraph node for shot agent"""
    import asyncio
    
    script = state.get("script")
    num_images = state.get("num_images", 6)
    
    if not script:
        raise ValueError("No script available for shot generation")
    
    shots = asyncio.run(generate_shots(script, num_images))
    
    return {
        **state,
        "shots": shots
    }
