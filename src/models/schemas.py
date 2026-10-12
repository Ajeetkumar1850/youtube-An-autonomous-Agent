"""
Pydantic models for data validation and serialization
Enhanced with comprehensive video generation parameters
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict, validator


class VideoStatus(str, Enum):
    """Video generation pipeline status"""
    PENDING = "pending"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    GENERATING_SHOTS = "generating_shots"
    GENERATING_IMAGES = "generating_images"
    GENERATING_VOICE = "generating_voice"
    GENERATING_SUBTITLES = "generating_subtitles"  # NEW
    CREATING_VIDEO = "creating_video"
    ADDING_BGM = "adding_bgm"  # NEW
    GENERATING_SEO = "generating_seo"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoAspectRatio(str, Enum):
    """Supported video aspect ratios"""
    VERTICAL = "9:16"      # TikTok, YouTube Shorts
    HORIZONTAL = "16:9"    # YouTube, landscape
    SQUARE = "1:1"         # Instagram


class VideoTransition(str, Enum):
    """Video transition effects"""
    NONE = "none"
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    DISSOLVE = "dissolve"


class TTSProvider(str, Enum):
    """Text-to-Speech providers"""
    EDGE = "edge"           # Free, default
    AZURE = "azure"         # Enterprise
    ELEVENLABS = "elevenlabs"  # Premium quality
    GOOGLE = "google"       # Good quality


class SubtitleProvider(str, Enum):
    """Subtitle generation providers"""
    EDGE = "edge"           # Fast, uses TTS timestamps
    WHISPER = "whisper"     # Accurate, uses transcription


class VideoSource(str, Enum):
    """Video material sources"""
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    LOCAL = "local"


@dataclass
class MaterialInfo:
    """Information about generated material (image/video)"""
    provider: str
    url: str
    duration: float
    type: str  # "image" or "video"
    metadata: Optional[Dict[str, Any]] = None


class VideoParams(BaseModel):
    """Complete video generation parameters - MoneyPrinterTurbo inspired"""
    
    # Script Settings
    video_subject: str = Field(..., min_length=1, max_length=200, description="Video topic/subject")
    video_script: Optional[str] = Field(None, description="Custom script (optional)")
    video_language: str = Field(default="hi", description="Video language code")
    paragraph_number: int = Field(default=6, ge=3, le=12, description="Number of scenes/shots")
    
    # Video Settings
    video_aspect: VideoAspectRatio = Field(default=VideoAspectRatio.VERTICAL, description="Video aspect ratio")
    video_concat_mode: str = Field(default="random", description="Scene concatenation mode")
    video_clip_duration: int = Field(default=5, ge=3, le=10, description="Duration per clip in seconds")
    video_clip_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Video playback speed")
    video_transition: VideoTransition = Field(default=VideoTransition.FADE, description="Transition effect")
    
    # Voice/TTS Settings
    voice_provider: TTSProvider = Field(default=TTSProvider.EDGE, description="TTS provider")
    voice_name: str = Field(default="hi-IN-SwaraNeural", description="Voice model name")
    voice_volume: float = Field(default=1.0, ge=0.0, le=2.0, description="Voice volume multiplier")
    voice_rate: str = Field(default="+10%", description="Voice speed rate")
    
    # Subtitle Settings
    subtitle_enabled: bool = Field(default=False, description="Enable subtitles")
    subtitle_provider: SubtitleProvider = Field(default=SubtitleProvider.EDGE, description="Subtitle provider")
    subtitle_position: str = Field(default="bottom", description="Subtitle position")
    font_name: str = Field(default="Arial", description="Subtitle font")
    font_size: int = Field(default=60, ge=20, le=120, description="Subtitle font size")
    text_color: str = Field(default="#FFFFFF", description="Subtitle text color")
    stroke_color: str = Field(default="#000000", description="Subtitle stroke color")
    stroke_width: float = Field(default=1.5, ge=0.0, le=5.0, description="Subtitle stroke width")
    
    # Background Music
    bgm_enabled: bool = Field(default=False, description="Enable background music")
    bgm_type: str = Field(default="random", description="BGM selection type")
    bgm_file: Optional[str] = Field(None, description="Custom BGM file path")
    bgm_volume: float = Field(default=0.2, ge=0.0, le=1.0, description="BGM volume (0-1)")
    
    # Material Settings
    video_source: VideoSource = Field(default=VideoSource.LOCAL, description="Video/image source")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "video_subject": "motivation",
            "paragraph_number": 6,
            "video_aspect": "9:16",
            "voice_provider": "edge",
            "subtitle_enabled": False,
            "bgm_enabled": False
        }
    })


class VideoRequest(BaseModel):
    """Simplified request to create a video (backward compatible)"""
    niche: str = Field(..., min_length=1, max_length=200, description="Video niche/topic")
    num_images: int = Field(default=6, ge=3, le=12, description="Number of images to generate")
    
    # Optional advanced parameters
    params: Optional[VideoParams] = Field(None, description="Advanced video parameters")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "niche": "motivation",
            "num_images": 6
        }
    })


class VideoResponse(BaseModel):
    """Response after creating video job"""
    job_id: str = Field(..., description="Unique job identifier")
    status: VideoStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "pending",
            "message": "Video generation job created",
            "created_at": "2024-01-01T12:00:00"
        }
    })


class VideoStatusResponse(BaseModel):
    """Video job status response"""
    job_id: str
    status: VideoStatus
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current pipeline step")
    error: Optional[str] = Field(None, description="Error message if failed")
    video_url: Optional[str] = Field(None, description="Video URL if completed")
    youtube_url: Optional[str] = Field(None, description="YouTube URL if uploaded")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "generating_images",
            "progress": 45,
            "current_step": "Generating image 3/6",
            "error": None,
            "video_url": None,
            "youtube_url": None,
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:05:00"
        }
    })


class AgentState(BaseModel):
    """State passed between agents in LangGraph"""
    job_id: str
    niche: str
    num_images: int
    
    # Research Agent Output
    topics: Optional[List[str]] = None
    selected_topic: Optional[str] = None
    
    # Script Agent Output
    script: Optional[str] = None
    
    # Shot Agent Output
    shots: Optional[List[str]] = None
    
    # Image Agent Output
    image_paths: Optional[List[str]] = None
    
    # Voice Agent Output
    audio_path: Optional[str] = None
    
    # Video Agent Output
    video_path: Optional[str] = None
    
    # SEO Agent Output
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_tags: Optional[List[str]] = None
    seo_hashtags: Optional[List[str]] = None
    
    # Upload Agent Output
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    
    # Error tracking
    error: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: dict = Field(..., description="Status of dependent services")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00",
            "services": {
                "database": "connected",
                "redis": "connected",
                "ollama": "running"
            }
        }
    })


class MetricsResponse(BaseModel):
    """Prometheus metrics response"""
    total_videos: int
    completed_videos: int
    failed_videos: int
    average_duration_seconds: float
    cache_hit_rate: float
