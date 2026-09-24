"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/youtube_agent",
        description="PostgreSQL connection string"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    # LLM
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(default="llama3", description="Ollama model name")
    
    # Image Generation
    image_api_url: str = Field(
        default="https://image.pollinations.ai/prompt",
        description="Image generation API URL"
    )
    image_api_timeout: int = Field(
        default=90,
        description="Image API timeout in seconds"
    )
    
    # Voice
    voice_model: str = Field(
        default="hi-IN-SwaraNeural",
        description="Edge TTS voice model"
    )
    voice_rate: str = Field(default="+10%", description="Voice speed rate")
    
    # Video
    video_fps: int = Field(default=24, description="Video frames per second")
    video_bitrate: str = Field(default="2500k", description="Video bitrate")
    video_preset: str = Field(
        default="ultrafast",
        description="FFmpeg encoding preset"
    )
    
    # YouTube
    youtube_client_secret_path: str = Field(
        default="client_secret.json",
        description="YouTube OAuth client secret file"
    )
    youtube_category_id: str = Field(
        default="22",
        description="YouTube video category ID"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Storage
    scenes_dir: str = Field(default="scenes", description="Scene images directory")
    audio_dir: str = Field(default="audio", description="Audio files directory")
    videos_dir: str = Field(default="videos", description="Video files directory")


# Global settings instance
settings = Settings()
