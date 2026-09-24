"""
Database models using SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum, Float
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from src.models.schemas import VideoStatus


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    pass


class VideoJob(Base):
    """Video generation job table"""
    __tablename__ = "video_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, index=True, nullable=False)
    
    # Input
    niche = Column(String(200), nullable=False)
    num_images = Column(Integer, default=6)
    
    # Status
    status = Column(
        SQLEnum(VideoStatus),
        default=VideoStatus.PENDING,
        nullable=False,
        index=True
    )
    progress = Column(Integer, default=0)
    current_step = Column(String(200))
    error = Column(Text, nullable=True)
    
    # Outputs
    topics = Column(Text, nullable=True)
    selected_topic = Column(String(500), nullable=True)
    script = Column(Text, nullable=True)
    shots = Column(Text, nullable=True)
    image_paths = Column(Text, nullable=True)
    audio_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    
    # SEO
    seo_title = Column(String(200), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_tags = Column(Text, nullable=True)
    seo_hashtags = Column(Text, nullable=True)
    
    # YouTube
    youtube_video_id = Column(String(50), nullable=True)
    youtube_url = Column(String(200), nullable=True)
    
    # Metrics
    duration_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<VideoJob(job_id={self.job_id}, status={self.status})>"
