"""
Pydantic models for data validation and serialization
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class VideoStatus(str, Enum):
    """Video generation pipeline status"""
    PENDING = "pending"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    GENERATING_SHOTS = "generating_shots"
    GENERATING_IMAGES = "generating_images"
    GENERATING_VOICE = "generating_voice"
    CREATING_VIDEO = "creating_video"
    GENERATING_SEO = "generating_seo"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoRequest(BaseModel):
    """Request to create a video"""
    niche: str = Field(..., min_length=1, max_length=200, description="Video niche/topic")
    num_images: int = Field(default=6, ge=3, le=12, description="Number of images to generate")
    
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
