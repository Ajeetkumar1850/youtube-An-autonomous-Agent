"""
Video Agent - Upgraded with better error handling and async support
"""
import os
import random
from typing import Dict, List
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video import fx as vfx
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from src.config import settings

logger = structlog.get_logger()


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=5, max=20),
    reraise=True
)
def create_video(image_paths: List[str], audio_path: str) -> str:
    """
    Create dynamic animated video from images and audio
    """
    logger.info(
        "video_agent_started",
        num_images=len(image_paths),
        audio_path=audio_path
    )
    
    if not image_paths:
        raise ValueError("No images provided for video creation")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Create videos folder
    os.makedirs(settings.videos_dir, exist_ok=True)
    
    try:
        # Load audio
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        
        logger.info("audio_loaded", duration_seconds=audio_duration)
        
        # Calculate shot duration
        duration_per_shot = audio_duration / len(image_paths)
        
        logger.info(
            "creating_clips",
            duration_per_shot=duration_per_shot,
            total_duration=audio_duration
        )
        
        clips = []
        animation_styles = [
            "talking_zoom",
            "action_pan",
            "emotion_pulse",
            "walk_slide",
            "dramatic_zoom"
        ]
        
        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                logger.warning("image_not_found", path=image_path)
                continue
            
            # Base clip
            clip = (
                ImageClip(image_path)
                .set_duration(duration_per_shot)
                .resize(height=1920)
            )
            
            # Random animation style
            animation = random.choice(animation_styles)
            
            # Apply animation
            if animation == "talking_zoom":
                # Subtle zoom pulse for talking
                clip = clip.resize(lambda t: 1.05 + 0.03 * (t % 0.5))
                
            elif animation == "action_pan":
                # Horizontal movement
                clip = clip.resize(1.15)
                clip = clip.set_position(
                    lambda t: (-100 + (t / duration_per_shot) * 200, "center")
                )
                
            elif animation == "emotion_pulse":
                # Slow zoom for emotion
                clip = clip.resize(lambda t: 1 + 0.2 * (t / duration_per_shot))
                clip = clip.fx(vfx.colorx, 1.15)
                
            elif animation == "walk_slide":
                # Diagonal movement for walking
                clip = clip.resize(1.2)
                clip = clip.set_position(
                    lambda t: (
                        -(t / duration_per_shot) * 150,
                        50 - (t / duration_per_shot) * 100
                    )
                )
                
            elif animation == "dramatic_zoom":
                # Fast zoom in
                clip = clip.resize(lambda t: 1 + 0.25 * (t / duration_per_shot))
            
            # Smooth transitions
            clip = clip.fadein(0.3).fadeout(0.3)
            
            # Random brightness
            if i % 4 == 0:
                clip = clip.fx(vfx.colorx, 1.1)
            
            clips.append(clip)
            
            logger.debug(
                "clip_created",
                index=i + 1,
                animation=animation,
                duration=duration_per_shot
            )
        
        if not clips:
            raise ValueError("No valid clips created from images")
        
        # Combine clips
        logger.info("concatenating_clips", num_clips=len(clips))
        video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        video = video.set_audio(audio)
        
        # Export
        output_path = os.path.join(settings.videos_dir, "final_video.mp4")
        
        logger.info("exporting_video", output_path=output_path)
        
        video.write_videofile(
            output_path,
            fps=settings.video_fps,
            codec="libx264",
            audio_codec="aac",
            preset=settings.video_preset,
            threads=2,
            bitrate=settings.video_bitrate,
            logger=None  # Disable MoviePy's verbose logging
        )
        
        # Verify output
        if not os.path.exists(output_path):
            raise FileNotFoundError("Video file was not created")
        
        file_size = os.path.getsize(output_path)
        
        logger.info(
            "video_agent_completed",
            output_path=output_path,
            size_mb=file_size / (1024 * 1024),
            duration_seconds=audio_duration
        )
        
        # Cleanup
        video.close()
        audio.close()
        for clip in clips:
            clip.close()
        
        return output_path
        
    except Exception as e:
        logger.error("video_creation_failed", error=str(e), exc_info=True)
        raise


def video_agent_node(state: Dict) -> Dict:
    """LangGraph node for video agent"""
    image_paths = state.get("image_paths")
    audio_path = state.get("audio_path")
    
    if not image_paths:
        raise ValueError("No images available for video creation")
    
    if not audio_path:
        raise ValueError("No audio available for video creation")
    
    video_path = create_video(image_paths, audio_path)
    
    return {
        **state,
        "video_path": video_path
    }
