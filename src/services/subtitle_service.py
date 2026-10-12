"""
Subtitle Generation Service
Supports: Edge TTS timestamps, Whisper transcription
"""
import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class SubtitleSegment:
    """Single subtitle segment"""
    start: float  # Start time in seconds
    end: float    # End time in seconds
    text: str     # Subtitle text


class SubtitleProvider(ABC):
    """Base class for subtitle providers"""
    
    @abstractmethod
    async def generate(
        self,
        audio_path: str,
        mode: str = "sentence"
    ) -> List[SubtitleSegment]:
        """Generate subtitles from audio"""
        pass


class EdgeSubtitleProvider(SubtitleProvider):
    """Generate subtitles from Edge TTS timestamps"""
    
    async def generate(
        self,
        audio_path: str,
        mode: str = "sentence"
    ) -> List[SubtitleSegment]:
        """
        Generate subtitles using Edge TTS word timestamps
        Note: This requires the original text used for TTS
        """
        logger.info("edge_subtitle_generating", audio_path=audio_path)
        
        # For Edge TTS, we need the original text and voice
        # This is a simplified version - in production, you'd store
        # the timestamp data from the TTS generation
        
        # Placeholder implementation
        # In real usage, you'd capture timestamps during TTS generation
        segments = []
        
        logger.warning("edge_subtitle_not_fully_implemented")
        
        return segments


class WhisperSubtitleProvider(SubtitleProvider):
    """Generate subtitles using Whisper transcription"""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
    
    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                
                logger.info(
                    "loading_whisper_model",
                    model_size=self.model_size,
                    device=self.device
                )
                
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                
                logger.info("whisper_model_loaded")
                
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. "
                    "Install with: pip install faster-whisper"
                )
    
    async def generate(
        self,
        audio_path: str,
        mode: str = "sentence"
    ) -> List[SubtitleSegment]:
        """
        Generate subtitles using Whisper transcription
        
        Args:
            audio_path: Path to audio file
            mode: "word" for word-level, "sentence" for sentence-level
        
        Returns:
            List of subtitle segments
        """
        logger.info(
            "whisper_subtitle_generating",
            audio_path=audio_path,
            mode=mode
        )
        
        self._load_model()
        
        try:
            # Transcribe with word-level timestamps
            segments, info = self.model.transcribe(
                audio_path,
                word_timestamps=(mode == "word"),
                language="hi"  # Default to Hindi, make configurable
            )
            
            logger.info(
                "whisper_transcription_info",
                language=info.language,
                language_probability=info.language_probability,
                duration=info.duration
            )
            
            subtitle_segments = []
            
            if mode == "word":
                # Word-level subtitles
                for segment in segments:
                    if hasattr(segment, 'words') and segment.words:
                        for word in segment.words:
                            subtitle_segments.append(
                                SubtitleSegment(
                                    start=word.start,
                                    end=word.end,
                                    text=word.word.strip()
                                )
                            )
            else:
                # Sentence-level subtitles
                for segment in segments:
                    subtitle_segments.append(
                        SubtitleSegment(
                            start=segment.start,
                            end=segment.end,
                            text=segment.text.strip()
                        )
                    )
            
            logger.info(
                "whisper_subtitle_completed",
                num_segments=len(subtitle_segments)
            )
            
            return subtitle_segments
            
        except Exception as e:
            logger.error("whisper_subtitle_failed", error=str(e))
            raise


class SubtitleService:
    """
    Unified subtitle service supporting multiple providers
    """
    
    def __init__(
        self,
        provider: str = "whisper",
        whisper_model_size: str = "base",
        whisper_device: str = "cpu",
        whisper_compute_type: str = "int8"
    ):
        self.provider_name = provider.lower()
        
        # Initialize providers
        self.providers = {
            "edge": EdgeSubtitleProvider(),
            "whisper": WhisperSubtitleProvider(
                model_size=whisper_model_size,
                device=whisper_device,
                compute_type=whisper_compute_type
            )
        }
        
        if self.provider_name not in self.providers:
            logger.warning(
                f"Provider '{self.provider_name}' not available, using Whisper"
            )
            self.provider_name = "whisper"
    
    async def generate(
        self,
        audio_path: str,
        mode: str = "sentence"
    ) -> List[SubtitleSegment]:
        """
        Generate subtitles from audio
        
        Args:
            audio_path: Path to audio file
            mode: "word" for word-level, "sentence" for sentence-level
        
        Returns:
            List of subtitle segments
        """
        provider = self.providers[self.provider_name]
        
        logger.info(
            "subtitle_service_generating",
            provider=self.provider_name,
            audio_path=audio_path,
            mode=mode
        )
        
        segments = await provider.generate(audio_path, mode)
        
        return segments
    
    def segments_to_srt(self, segments: List[SubtitleSegment]) -> str:
        """
        Convert subtitle segments to SRT format
        
        Args:
            segments: List of subtitle segments
        
        Returns:
            SRT formatted string
        """
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            # Format timestamps (HH:MM:SS,mmm)
            start_time = self._format_timestamp(segment.start)
            end_time = self._format_timestamp(segment.end)
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text)
            srt_content.append("")  # Empty line between segments
        
        return "\n".join(srt_content)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    async def save_srt(
        self,
        audio_path: str,
        output_path: str,
        mode: str = "sentence"
    ) -> str:
        """
        Generate and save subtitles as SRT file
        
        Args:
            audio_path: Path to audio file
            output_path: Path to save SRT file
            mode: "word" or "sentence"
        
        Returns:
            Path to saved SRT file
        """
        segments = await self.generate(audio_path, mode)
        srt_content = self.segments_to_srt(segments)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        logger.info("srt_file_saved", output_path=output_path)
        
        return output_path


# Helper function for backward compatibility
async def generate_subtitles(
    audio_path: str,
    output_path: str,
    provider: str = "whisper",
    mode: str = "sentence",
    **provider_config
) -> str:
    """
    Generate subtitle file from audio
    
    Example:
        # Whisper (default)
        await generate_subtitles("audio.wav", "subtitles.srt")
        
        # Whisper with custom model
        await generate_subtitles(
            "audio.wav", "subtitles.srt",
            provider="whisper",
            whisper_model_size="large-v3",
            whisper_device="cuda"
        )
    """
    service = SubtitleService(provider=provider, **provider_config)
    return await service.save_srt(audio_path, output_path, mode)
