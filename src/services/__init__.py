"""
Enhanced Services for YouTube Autonomous Agent V2

This module provides production-grade services:
- Multi-provider TTS (Edge, Azure, ElevenLabs, Google)
- Subtitle generation (Edge timestamps, Whisper transcription)
- Background music integration with audio mixing
- Video effects and transitions (professional video editing)
"""

from .tts_service import (
    TTSService,
    EdgeTTSProvider,
    AzureTTSProvider,
    ElevenLabsTTSProvider,
    GoogleTTSProvider,
    generate_voice_with_service
)

from .subtitle_service import (
    SubtitleService,
    SubtitleSegment,
    EdgeSubtitleProvider,
    WhisperSubtitleProvider,
    generate_subtitles
)

from .bgm_service import (
    BGMService,
    mix_voice_and_bgm
)

from .video_effects import (
    VideoTransitions,
    VideoEffects,
    AnimationPresets,
    VideoEffectsService,
    apply_random_animation
)

__all__ = [
    # TTS
    "TTSService",
    "EdgeTTSProvider",
    "AzureTTSProvider",
    "ElevenLabsTTSProvider",
    "GoogleTTSProvider",
    "generate_voice_with_service",
    
    # Subtitles
    "SubtitleService",
    "SubtitleSegment",
    "EdgeSubtitleProvider",
    "WhisperSubtitleProvider",
    "generate_subtitles",
    
    # BGM
    "BGMService",
    "mix_voice_and_bgm",
    
    # Video Effects
    "VideoTransitions",
    "VideoEffects",
    "AnimationPresets",
    "VideoEffectsService",
    "apply_random_animation",
]
