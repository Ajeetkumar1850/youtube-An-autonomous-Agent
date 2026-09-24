"""
Voice Agent - Upgraded with async and better text cleaning
"""
import os
import re
from typing import Dict
import edge_tts
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.config import settings

logger = structlog.get_logger()


def clean_script_for_tts(script: str) -> str:
    """
    Clean script text for TTS processing
    """
    # Remove markdown formatting
    cleaned = script.replace("*", "")
    cleaned = cleaned.replace("#", "")
    cleaned = cleaned.replace("_", "")
    cleaned = cleaned.replace("**", "")
    
    # Remove newlines
    cleaned = cleaned.replace("\n", " ")
    
    # Remove numbers
    cleaned = re.sub(r'\d+', '', cleaned)
    
    # Remove extra spaces
    cleaned = " ".join(cleaned.split())
    
    # Remove emojis
    cleaned = re.sub(r'[^\w\s\u0900-\u097F,।?.!]', '', cleaned)
    
    return cleaned.strip()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_voice(script: str) -> str:
    """
    Generate voice using Edge TTS
    """
    logger.info("voice_agent_started", script_length=len(script))
    
    # Create audio folder
    os.makedirs(settings.audio_dir, exist_ok=True)
    
    output_file = os.path.join(settings.audio_dir, "output.wav")
    
    # Clean the script
    cleaned_script = clean_script_for_tts(script)
    
    if not cleaned_script:
        raise ValueError("Script is empty after cleaning")
    
    logger.info(
        "script_cleaned",
        original_length=len(script),
        cleaned_length=len(cleaned_script)
    )
    
    try:
        # Create TTS communication
        communicate = edge_tts.Communicate(
            text=cleaned_script,
            voice=settings.voice_model,
            rate=settings.voice_rate
        )
        
        # Save audio
        await communicate.save(output_file)
        
        # Verify file exists and has content
        if not os.path.exists(output_file):
            raise FileNotFoundError("Voice file was not created")
        
        file_size = os.path.getsize(output_file)
        if file_size == 0:
            raise ValueError("Voice file is empty")
        
        logger.info(
            "voice_agent_completed",
            output_file=output_file,
            size_bytes=file_size
        )
        
        return output_file
        
    except Exception as e:
        logger.error("voice_generation_failed", error=str(e))
        raise


def voice_agent_node(state: Dict) -> Dict:
    """LangGraph node for voice agent"""
    import asyncio
    
    script = state.get("script")
    
    if not script:
        raise ValueError("No script available for voice generation")
    
    audio_path = asyncio.run(generate_voice(script))
    
    return {
        **state,
        "audio_path": audio_path
    }
