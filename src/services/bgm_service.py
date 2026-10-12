"""
Background Music (BGM) Service
Handles background music selection and audio mixing
"""
import os
import random
from typing import Optional
from pathlib import Path
import structlog
from moviepy.editor import AudioFileClip, CompositeAudioClip

logger = structlog.get_logger()


class BGMService:
    """
    Background Music Service for video generation
    """
    
    def __init__(self, music_dir: str = "resource/songs"):
        self.music_dir = music_dir
        self._ensure_music_dir()
    
    def _ensure_music_dir(self):
        """Create music directory if it doesn't exist"""
        os.makedirs(self.music_dir, exist_ok=True)
        
        # Create a README if directory is empty
        readme_path = os.path.join(self.music_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write("""# Background Music Directory

Place your background music files here.

Supported formats:
- MP3
- WAV
- M4A
- OGG

The BGM service will randomly select from available music files.
""")
    
    def get_available_music(self) -> list:
        """Get list of available music files"""
        music_extensions = [".mp3", ".wav", ".m4a", ".ogg"]
        music_files = []
        
        if os.path.exists(self.music_dir):
            for file in os.listdir(self.music_dir):
                if any(file.lower().endswith(ext) for ext in music_extensions):
                    music_files.append(os.path.join(self.music_dir, file))
        
        return music_files
    
    def get_bgm(
        self,
        bgm_type: str = "random",
        custom_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Get background music file path
        
        Args:
            bgm_type: Type of BGM selection ("random", "custom", "none")
            custom_file: Path to custom BGM file (used when bgm_type="custom")
        
        Returns:
            Path to BGM file or None
        """
        logger.info("bgm_selection", bgm_type=bgm_type)
        
        if bgm_type == "none":
            return None
        
        if bgm_type == "custom":
            if custom_file and os.path.exists(custom_file):
                logger.info("bgm_selected_custom", file=custom_file)
                return custom_file
            else:
                logger.warning("bgm_custom_file_not_found", file=custom_file)
                return None
        
        if bgm_type == "random":
            music_files = self.get_available_music()
            
            if not music_files:
                logger.warning("bgm_no_music_available", music_dir=self.music_dir)
                return None
            
            selected = random.choice(music_files)
            logger.info("bgm_selected_random", file=selected)
            return selected
        
        return None
    
    def mix_audio(
        self,
        voice_audio_path: str,
        bgm_audio_path: Optional[str],
        output_path: str,
        voice_volume: float = 1.0,
        bgm_volume: float = 0.2,
        apply_ducking: bool = True
    ) -> str:
        """
        Mix voice and background music
        
        Args:
            voice_audio_path: Path to voice audio file
            bgm_audio_path: Path to BGM audio file (None to skip BGM)
            output_path: Path to save mixed audio
            voice_volume: Voice volume multiplier (0.0 to 2.0)
            bgm_volume: BGM volume multiplier (0.0 to 1.0)
            apply_ducking: Apply ducking (reduce BGM when voice plays)
        
        Returns:
            Path to mixed audio file
        """
        logger.info(
            "audio_mixing_started",
            voice_audio=voice_audio_path,
            bgm_audio=bgm_audio_path,
            voice_volume=voice_volume,
            bgm_volume=bgm_volume
        )
        
        try:
            # Load voice audio
            voice_clip = AudioFileClip(voice_audio_path)
            
            # Adjust voice volume
            if voice_volume != 1.0:
                voice_clip = voice_clip.volumex(voice_volume)
            
            # If no BGM, just save voice audio
            if not bgm_audio_path or not os.path.exists(bgm_audio_path):
                logger.info("audio_mixing_no_bgm", output_path=output_path)
                voice_clip.write_audiofile(output_path, codec='pcm_s16le')
                voice_clip.close()
                return output_path
            
            # Load BGM
            bgm_clip = AudioFileClip(bgm_audio_path)
            
            # Loop BGM if shorter than voice
            voice_duration = voice_clip.duration
            if bgm_clip.duration < voice_duration:
                # Calculate how many times to loop
                loops = int(voice_duration / bgm_clip.duration) + 1
                bgm_clips = [bgm_clip] * loops
                from moviepy.editor import concatenate_audioclips
                bgm_clip = concatenate_audioclips(bgm_clips)
            
            # Trim BGM to match voice duration
            bgm_clip = bgm_clip.subclip(0, voice_duration)
            
            # Apply ducking if enabled
            if apply_ducking:
                # Simple ducking: reduce BGM volume further when voice plays
                bgm_volume_ducked = bgm_volume * 0.5
                bgm_clip = bgm_clip.volumex(bgm_volume_ducked)
            else:
                bgm_clip = bgm_clip.volumex(bgm_volume)
            
            # Composite audio (mix voice and BGM)
            final_audio = CompositeAudioClip([voice_clip, bgm_clip])
            
            # Save mixed audio
            final_audio.write_audiofile(output_path, codec='pcm_s16le')
            
            # Clean up
            voice_clip.close()
            bgm_clip.close()
            final_audio.close()
            
            logger.info("audio_mixing_completed", output_path=output_path)
            
            return output_path
            
        except Exception as e:
            logger.error("audio_mixing_failed", error=str(e))
            
            # Fallback: use voice audio only
            logger.info("audio_mixing_fallback_to_voice_only")
            voice_clip = AudioFileClip(voice_audio_path)
            voice_clip.write_audiofile(output_path, codec='pcm_s16le')
            voice_clip.close()
            
            return output_path


# Helper function for backward compatibility
def mix_voice_and_bgm(
    voice_path: str,
    output_path: str,
    bgm_type: str = "random",
    bgm_custom_file: Optional[str] = None,
    bgm_volume: float = 0.2,
    voice_volume: float = 1.0,
    music_dir: str = "resource/songs"
) -> str:
    """
    Mix voice with background music
    
    Example:
        # Random BGM
        mix_voice_and_bgm("voice.wav", "mixed.wav")
        
        # Custom BGM
        mix_voice_and_bgm(
            "voice.wav", "mixed.wav",
            bgm_type="custom",
            bgm_custom_file="my_music.mp3"
        )
        
        # No BGM
        mix_voice_and_bgm("voice.wav", "mixed.wav", bgm_type="none")
    """
    service = BGMService(music_dir=music_dir)
    
    bgm_path = service.get_bgm(bgm_type, bgm_custom_file)
    
    return service.mix_audio(
        voice_audio_path=voice_path,
        bgm_audio_path=bgm_path,
        output_path=output_path,
        voice_volume=voice_volume,
        bgm_volume=bgm_volume
    )
