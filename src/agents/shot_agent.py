"""
Shot Agent - Using Groq API
"""
import re
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.agents.llm_helper import generate_with_cache

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_shots(script: str, num_shots: int = 12) -> List[str]:
    """Generate shot descriptions"""
    logger.info("shot_agent_started", num_shots=num_shots)
    
    prompt = f"""Generate {num_shots} detailed image prompts for this Hindi script:

Script: {script}

Requirements:
- Cartoon/animated style character
- One scene description per line
- Character in motion with expressive face
- Colorful and vibrant
- Suitable for kids

Format: One shot description per line, no numbering."""
    
    try:
        response = await generate_with_cache(
            prompt=prompt,
            cache_key=f"shots:{script[:100]}"
        )
        
        # Clean and parse shots
        lines = response.split("\n")
        shots = []
        
        for line in lines:
            # Remove numbering
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^[-•*]\s*', '', line)
            line = line.strip()
            
            if line and len(line) > 10:
                shots.append(line)
        
        # Ensure minimum 8 shots
        if len(shots) < 8:
            default_shots = [
                "Cute cartoon character with big expressive eyes looking curious",
                "Animated character in colorful world with happy expression",
                "Character showing surprise with hands on face",
                "Magical scene with character dancing joyfully",
                "Character with friends in beautiful garden",
                "Emotional scene with character thinking deeply",
                "Action scene with character running excitedly",
                "Happy ending with character smiling brightly"
            ]
            shots.extend(default_shots[:(8 - len(shots))])
        
        logger.info("shot_agent_completed", shots_count=len(shots))
        return shots[:num_shots]
        
    except Exception as e:
        logger.error("shot_agent_failed", error=str(e))
        raise


def shot_agent_node(state: Dict) -> Dict:
    """LangGraph node"""
    import asyncio
    
    script = state.get("script")
    num_images = state.get("num_images", 6)
    
    shots = asyncio.run(generate_shots(script, num_images))
    
    return {
        **state,
        "shots": shots
    }
