"""
Voice Agent - Enhanced with Multi-Provider TTS Support
"""
import os
import re
from typing import Dict
import structlog
from src.config import settings
from src.services import TTSService

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


async def generate_voice(
    script: str,
    provider: str = None,
    voice: str = None,
    rate: str = None,
    volume: float = None
) -> str:
    """
    Generate voice using configured TTS provider with gTTS fallback
    
    Args:
        script: Text script to convert to speech
        provider: TTS provider (default: from config)
        voice: Voice model name (default: from config)
        rate: Speech rate (default: from config)
        volume: Voice volume (default: from config)
    
    Returns:
        Path to generated audio file
    """
    # Use config defaults if not specified
    provider = provider or settings.tts_provider
    voice = voice or settings.tts_voice
    rate = rate or settings.tts_rate
    volume = volume if volume is not None else settings.tts_volume
    
    logger.info(
        "voice_agent_started",
        script_length=len(script),
        provider=provider,
        voice=voice
    )
    
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
    
    # Try primary provider first
    try:
        # Initialize TTS service with provider credentials
        tts_service = TTSService(
            provider=provider,
            azure_key=settings.azure_speech_key,
            azure_region=settings.azure_speech_region,
            elevenlabs_key=settings.elevenlabs_api_key,
            google_credentials=settings.google_credentials_path
        )
        
        # Generate speech
        result = await tts_service.generate(
            text=cleaned_script,
            voice=voice,
            output_path=output_file,
            rate=rate,
            volume=volume
        )
        
        # Verify output
        if not os.path.exists(result):
            raise FileNotFoundError("Voice file was not created")
        
        file_size = os.path.getsize(result)
        if file_size == 0:
            raise ValueError("Voice file is empty")
        
        logger.info(
            "voice_agent_completed",
            output_file=result,
            size_bytes=file_size,
            provider=provider
        )
        
        return result
        
    except Exception as e:
        logger.error("primary_tts_failed", error=str(e), provider=provider)
        logger.info("falling_back_to_gtts")
        
        # Fallback to gTTS
        try:
            from gtts import gTTS
            import tempfile
            
            # Detect language (default to English)
            lang = 'en'
            if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in cleaned_script):
                lang = 'hi'  # Hindi
            
            logger.info(f"Using gTTS fallback with lang={lang}")
            
            # Generate with gTTS
            tts = gTTS(text=cleaned_script, lang=lang, slow=False)
            
            # Save as MP3 first
            temp_mp3 = output_file.replace('.wav', '_temp.mp3')
            tts.save(temp_mp3)
            
            # Convert MP3 to WAV using moviepy
            from moviepy.editor import AudioFileClip
            audio_clip = AudioFileClip(temp_mp3)
            audio_clip.write_audiofile(output_file, codec='pcm_s16le', logger=None)
            audio_clip.close()
            
            # Clean up temp file
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            
            logger.info("gtts_fallback_completed", output_file=output_file)
            return output_file
            
        except Exception as gtts_error:
            logger.error("gtts_fallback_failed", error=str(gtts_error))
            raise Exception(f"Both TTS providers failed. Primary: {e}, gTTS: {gtts_error}")


async def generate_voice_with_bgm(
    script: str,
    bgm_enabled: bool = None,
    bgm_type: str = None,
    bgm_volume: float = None,
    **tts_kwargs
) -> str:
    """
    Generate voice with optional background music
    
    Args:
        script: Text script
        bgm_enabled: Enable BGM (default: from config)
        bgm_type: BGM type - "random", "custom", "none"
        bgm_volume: BGM volume (default: from config)
        **tts_kwargs: Additional TTS parameters
    
    Returns:
        Path to audio file (with or without BGM)
    """
    from src.services import BGMService
    
    # Generate voice
    voice_path = await generate_voice(script, **tts_kwargs)
    
    # Check if BGM is enabled
    bgm_enabled = bgm_enabled if bgm_enabled is not None else settings.bgm_enabled
    
    if not bgm_enabled:
        logger.info("bgm_disabled", voice_path=voice_path)
        return voice_path
    
    # Mix with BGM
    bgm_type = bgm_type or settings.bgm_type
    bgm_volume = bgm_volume if bgm_volume is not None else settings.bgm_volume
    
    logger.info("mixing_with_bgm", bgm_type=bgm_type, bgm_volume=bgm_volume)
    
    try:
        bgm_service = BGMService(music_dir=settings.bgm_music_dir)
        
        # Get BGM file
        bgm_path = bgm_service.get_bgm(bgm_type=bgm_type)
        
        if not bgm_path:
            logger.warning("no_bgm_available", returning_voice_only=True)
            return voice_path
        
        # Mix audio
        mixed_path = os.path.join(settings.audio_dir, "output_with_bgm.wav")
        result = bgm_service.mix_audio(
            voice_audio_path=voice_path,
            bgm_audio_path=bgm_path,
            output_path=mixed_path,
            voice_volume=1.0,
            bgm_volume=bgm_volume,
            apply_ducking=True
        )
        
        logger.info("bgm_mixed_successfully", output=result)
        return result
        
    except Exception as e:
        logger.error("bgm_mixing_failed", error=str(e))
        logger.info("fallback_to_voice_only")
        return voice_path


def voice_agent_node(state: Dict) -> Dict:
    """LangGraph node for voice agent"""
    import asyncio
    
    script = state.get("script")
    
    if not script:
        raise ValueError("No script available for voice generation")
    
    # Check if BGM is enabled in state or config
    bgm_enabled = state.get("bgm_enabled", settings.bgm_enabled)
    
    if bgm_enabled:
        audio_path = asyncio.run(generate_voice_with_bgm(script))
    else:
        audio_path = asyncio.run(generate_voice(script))
    
    return {
        **state,
        "audio_path": audio_path
    }

