"""
Configuration management with TOML support + Pydantic Settings
"""
import os
import toml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


def load_toml_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file"""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return toml.load(f)
    return {}


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # App
    app_name: str = Field(default="YouTube Autonomous Agent V2", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    app_debug: bool = Field(default=False, description="Debug mode")
    
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
    redis_cache_ttl: int = Field(default=86400, description="Cache TTL in seconds")
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    # LLM
    llm_provider: str = Field(default="groq", description="LLM provider")
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    ollama_model: str = Field(default="llama3", description="Ollama model name")
    llm_temperature: float = Field(default=0.7, description="LLM temperature")
    llm_max_tokens: int = Field(default=2000, description="LLM max tokens")
    
    # LLM API Keys
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    together_api_key: Optional[str] = Field(default=None, description="Together AI API key")
    
    # TTS
    tts_provider: str = Field(default="edge", description="TTS provider")
    tts_voice: str = Field(
        default="hi-IN-SwaraNeural",
        description="Default voice model"
    )
    tts_rate: str = Field(default="+10%", description="Voice speed rate")
    tts_volume: float = Field(default=1.0, description="Voice volume")
    
    # TTS Providers
    azure_speech_key: Optional[str] = Field(default=None, description="Azure Speech API key")
    azure_speech_region: Optional[str] = Field(default=None, description="Azure Speech region")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key")
    google_credentials_path: Optional[str] = Field(default=None, description="Google credentials JSON path")
    
    # Subtitle
    subtitle_provider: str = Field(default="whisper", description="Subtitle provider")
    subtitle_enabled: bool = Field(default=False, description="Enable subtitles")
    subtitle_position: str = Field(default="bottom", description="Subtitle position")
    subtitle_mode: str = Field(default="sentence", description="Subtitle mode")
    whisper_model_size: str = Field(default="base", description="Whisper model size")
    whisper_device: str = Field(default="cpu", description="Whisper device")
    whisper_compute_type: str = Field(default="int8", description="Whisper compute type")
    
    # Image Generation
    image_api_url: str = Field(
        default="https://image.pollinations.ai/prompt",
        description="Image generation API URL"
    )
    image_api_timeout: int = Field(
        default=90,
        description="Image API timeout in seconds"
    )
    
    # Video
    video_fps: int = Field(default=24, description="Video frames per second")
    video_bitrate: str = Field(default="2500k", description="Video bitrate")
    video_preset: str = Field(
        default="ultrafast",
        description="FFmpeg encoding preset"
    )
    video_aspect_ratio: str = Field(default="9:16", description="Video aspect ratio")
    video_transition: str = Field(default="fade", description="Video transition effect")
    
    # BGM
    bgm_enabled: bool = Field(default=False, description="Enable background music")
    bgm_type: str = Field(default="random", description="BGM selection type")
    bgm_volume: float = Field(default=0.2, description="BGM volume")
    bgm_music_dir: str = Field(default="resource/songs", description="BGM music directory")
    
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
    cache_dir: str = Field(default=".cache", description="Cache directory")


def create_settings() -> Settings:
    """Create settings instance with TOML config overlay"""
    # Load TOML config
    toml_config = load_toml_config()
    
    # Flatten TOML config for Pydantic
    flat_config = {}
    
    if toml_config:
        # App settings
        if "app" in toml_config:
            flat_config["app_name"] = toml_config["app"].get("name", "YouTube Autonomous Agent V2")
            flat_config["app_version"] = toml_config["app"].get("version", "2.0.0")
            flat_config["app_debug"] = toml_config["app"].get("debug", False)
        
        # LLM settings
        if "llm" in toml_config:
            flat_config["llm_provider"] = toml_config["llm"].get("provider", "groq")
            flat_config["ollama_model"] = toml_config["llm"].get("model", "llama3")
            flat_config["ollama_base_url"] = toml_config["llm"].get("base_url", "http://localhost:11434")
            flat_config["llm_temperature"] = toml_config["llm"].get("temperature", 0.7)
            flat_config["llm_max_tokens"] = toml_config["llm"].get("max_tokens", 2000)
            
            # API Keys
            flat_config["groq_api_key"] = toml_config["llm"].get("groq_api_key")
            flat_config["gemini_api_key"] = toml_config["llm"].get("gemini_api_key")
            flat_config["together_api_key"] = toml_config["llm"].get("together_api_key")
        
        # TTS settings
        if "tts" in toml_config:
            flat_config["tts_provider"] = toml_config["tts"].get("provider", "edge")
            flat_config["tts_voice"] = toml_config["tts"].get("default_voice", "hi-IN-SwaraNeural")
            flat_config["tts_rate"] = toml_config["tts"].get("rate", "+10%")
            flat_config["tts_volume"] = toml_config["tts"].get("volume", 1.0)
        
        # Subtitle settings
        if "subtitle" in toml_config:
            flat_config["subtitle_provider"] = toml_config["subtitle"].get("provider", "whisper")
            flat_config["subtitle_enabled"] = toml_config["subtitle"].get("enabled", False)
            flat_config["subtitle_position"] = toml_config["subtitle"].get("position", "bottom")
            flat_config["subtitle_mode"] = toml_config["subtitle"].get("mode", "sentence")
            
            if "whisper" in toml_config["subtitle"]:
                flat_config["whisper_model_size"] = toml_config["subtitle"]["whisper"].get("model_size", "base")
                flat_config["whisper_device"] = toml_config["subtitle"]["whisper"].get("device", "cpu")
                flat_config["whisper_compute_type"] = toml_config["subtitle"]["whisper"].get("compute_type", "int8")
        
        # Video settings
        if "video" in toml_config:
            flat_config["video_fps"] = toml_config["video"].get("fps", 24)
            flat_config["video_bitrate"] = toml_config["video"].get("bitrate", "2500k")
            flat_config["video_preset"] = toml_config["video"].get("preset", "ultrafast")
            flat_config["video_aspect_ratio"] = toml_config["video"].get("aspect_ratio", "9:16")
            flat_config["video_transition"] = toml_config["video"].get("transition", "fade")
        
        # BGM settings
        if "bgm" in toml_config:
            flat_config["bgm_enabled"] = toml_config["bgm"].get("enabled", False)
            flat_config["bgm_type"] = toml_config["bgm"].get("type", "random")
            flat_config["bgm_volume"] = toml_config["bgm"].get("volume", 0.2)
            flat_config["bgm_music_dir"] = toml_config["bgm"].get("music_dir", "resource/songs")
        
        # Storage settings
        if "storage" in toml_config:
            flat_config["scenes_dir"] = toml_config["storage"].get("scenes_dir", "scenes")
            flat_config["audio_dir"] = toml_config["storage"].get("audio_dir", "audio")
            flat_config["videos_dir"] = toml_config["storage"].get("videos_dir", "videos")
            flat_config["cache_dir"] = toml_config["storage"].get("cache_dir", ".cache")
        
        # Database settings
        if "database" in toml_config:
            flat_config["database_url"] = toml_config["database"].get("url", "postgresql+asyncpg://user:password@localhost:5432/youtube_agent")
        
        # Redis settings
        if "redis" in toml_config:
            flat_config["redis_url"] = toml_config["redis"].get("url", "redis://localhost:6379/0")
            flat_config["redis_cache_ttl"] = toml_config["redis"].get("cache_ttl", 86400)
        
        # API settings
        if "api" in toml_config:
            flat_config["api_host"] = toml_config["api"].get("host", "0.0.0.0")
            flat_config["api_port"] = toml_config["api"].get("port", 8000)
    
    # Create settings with flat config
    return Settings(**flat_config)


# Global settings instance
settings = create_settings()
