"""
Video Effects and Transitions Service
Provides professional transitions and effects for video clips
"""
from typing import Optional, Callable
from moviepy.editor import VideoClip, ImageClip, CompositeVideoClip
import numpy as np
import structlog

logger = structlog.get_logger()


class VideoTransitions:
    """Professional video transitions"""
    
    @staticmethod
    def fade_in(clip: VideoClip, duration: float = 0.5) -> VideoClip:
        """Fade in transition"""
        return clip.fadein(duration)
    
    @staticmethod
    def fade_out(clip: VideoClip, duration: float = 0.5) -> VideoClip:
        """Fade out transition"""
        return clip.fadeout(duration)
    
    @staticmethod
    def crossfade(clip1: VideoClip, clip2: VideoClip, duration: float = 0.5) -> VideoClip:
        """Crossfade between two clips"""
        return clip1.crossfadeout(duration).crossfadein(duration)
    
    @staticmethod
    def slide_in(clip: VideoClip, duration: float = 0.5, direction: str = "left") -> VideoClip:
        """
        Slide in transition
        
        Args:
            clip: Video clip
            duration: Transition duration in seconds
            direction: "left", "right", "top", "bottom"
        """
        w, h = clip.size
        
        if direction == "left":
            # Slide from left
            pos_func = lambda t: (
                -w + (w * min(t / duration, 1)),
                0
            )
        elif direction == "right":
            # Slide from right
            pos_func = lambda t: (
                w - (w * min(t / duration, 1)),
                0
            )
        elif direction == "top":
            # Slide from top
            pos_func = lambda t: (
                0,
                -h + (h * min(t / duration, 1))
            )
        else:  # bottom
            # Slide from bottom
            pos_func = lambda t: (
                0,
                h - (h * min(t / duration, 1))
            )
        
        return clip.set_position(pos_func)
    
    @staticmethod
    def zoom_in(clip: VideoClip, start_scale: float = 1.0, end_scale: float = 1.2) -> VideoClip:
        """
        Zoom in effect over the entire clip duration
        
        Args:
            clip: Video clip
            start_scale: Starting scale (1.0 = original size)
            end_scale: Ending scale (1.2 = 20% larger)
        """
        duration = clip.duration
        
        def scale_func(t):
            progress = t / duration
            scale = start_scale + (end_scale - start_scale) * progress
            return scale
        
        return clip.resize(scale_func)
    
    @staticmethod
    def zoom_out(clip: VideoClip, start_scale: float = 1.2, end_scale: float = 1.0) -> VideoClip:
        """
        Zoom out effect over the entire clip duration
        """
        duration = clip.duration
        
        def scale_func(t):
            progress = t / duration
            scale = start_scale + (end_scale - start_scale) * progress
            return scale
        
        return clip.resize(scale_func)
    
    @staticmethod
    def ken_burns(
        clip: VideoClip,
        zoom_ratio: float = 0.2,
        pan_horizontal: float = 0.1,
        pan_vertical: float = 0.0
    ) -> VideoClip:
        """
        Ken Burns effect (slow zoom + pan)
        
        Args:
            clip: Video clip
            zoom_ratio: Amount of zoom (0.2 = 20% zoom)
            pan_horizontal: Horizontal pan (-1 to 1, 0 = no pan)
            pan_vertical: Vertical pan (-1 to 1, 0 = no pan)
        """
        duration = clip.duration
        w, h = clip.size
        
        def transform(t):
            progress = t / duration
            
            # Calculate zoom
            scale = 1.0 + (zoom_ratio * progress)
            
            # Calculate pan
            pan_x = w * pan_horizontal * progress
            pan_y = h * pan_vertical * progress
            
            return scale, (pan_x, pan_y)
        
        def resize_func(t):
            scale, _ = transform(t)
            return scale
        
        def pos_func(t):
            _, pos = transform(t)
            return pos
        
        return clip.resize(resize_func).set_position(pos_func)


class VideoEffects:
    """Video effects and filters"""
    
    @staticmethod
    def brightness(clip: VideoClip, factor: float = 1.2) -> VideoClip:
        """
        Adjust brightness
        
        Args:
            clip: Video clip
            factor: Brightness factor (1.0 = original, >1.0 = brighter, <1.0 = darker)
        """
        def brightness_filter(image):
            return np.clip(image * factor, 0, 255).astype('uint8')
        
        return clip.fl_image(brightness_filter)
    
    @staticmethod
    def blur(clip: VideoClip, blur_radius: int = 5) -> VideoClip:
        """
        Apply blur effect
        
        Args:
            clip: Video clip
            blur_radius: Blur radius in pixels
        """
        try:
            from PIL import Image, ImageFilter
            
            def blur_filter(image):
                pil_img = Image.fromarray(image)
                blurred = pil_img.filter(ImageFilter.GaussianBlur(blur_radius))
                return np.array(blurred)
            
            return clip.fl_image(blur_filter)
        except ImportError:
            logger.warning("PIL not available for blur effect")
            return clip
    
    @staticmethod
    def vignette(clip: VideoClip, intensity: float = 0.5) -> VideoClip:
        """
        Add vignette effect (darkened corners)
        
        Args:
            clip: Video clip
            intensity: Vignette intensity (0.0 to 1.0)
        """
        w, h = clip.size
        
        # Create vignette mask
        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        
        # Distance from center
        distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        max_distance = np.sqrt(cx ** 2 + cy ** 2)
        
        # Normalize and invert (1.0 at center, 0.0 at edges)
        vignette_mask = 1 - (distance / max_distance)
        
        # Apply intensity
        vignette_mask = 1 - (1 - vignette_mask) * intensity
        vignette_mask = np.clip(vignette_mask, 0, 1)
        
        # Reshape for RGB
        vignette_mask = vignette_mask[:, :, np.newaxis]
        
        def vignette_filter(image):
            return np.clip(image * vignette_mask, 0, 255).astype('uint8')
        
        return clip.fl_image(vignette_filter)
    
    @staticmethod
    def color_temperature(clip: VideoClip, temperature: float = 1.0) -> VideoClip:
        """
        Adjust color temperature
        
        Args:
            clip: Video clip
            temperature: Temperature (>1.0 = warmer/orange, <1.0 = cooler/blue)
        """
        def temp_filter(image):
            result = image.copy()
            if temperature > 1.0:
                # Warmer - increase red, decrease blue
                result[:, :, 0] = np.clip(result[:, :, 0] * temperature, 0, 255)
                result[:, :, 2] = np.clip(result[:, :, 2] / temperature, 0, 255)
            else:
                # Cooler - decrease red, increase blue
                result[:, :, 0] = np.clip(result[:, :, 0] * temperature, 0, 255)
                result[:, :, 2] = np.clip(result[:, :, 2] / temperature, 0, 255)
            return result.astype('uint8')
        
        return clip.fl_image(temp_filter)


class AnimationPresets:
    """Predefined animation presets for talking/action videos"""
    
    @staticmethod
    def talking_head(clip: VideoClip, intensity: float = 0.03) -> VideoClip:
        """
        Talking head animation - subtle pulse effect
        
        Args:
            clip: Image/video clip
            intensity: Pulse intensity (0.03 = 3% size variation)
        """
        duration = clip.duration
        
        def scale_func(t):
            # Oscillate at ~2 Hz (like talking)
            frequency = 2.0
            pulse = np.sin(2 * np.pi * frequency * t)
            scale = 1.0 + (intensity * pulse)
            return scale
        
        return clip.resize(scale_func)
    
    @staticmethod
    def action_pan(clip: VideoClip, distance: int = 300) -> VideoClip:
        """
        Action scene - horizontal pan
        
        Args:
            clip: Image/video clip
            distance: Pan distance in pixels
        """
        duration = clip.duration
        
        def pos_func(t):
            progress = t / duration
            x = -distance / 2 + (distance * progress)
            return (x, 0)
        
        return clip.set_position(pos_func)
    
    @staticmethod
    def emotion_pulse(clip: VideoClip, zoom_amount: float = 0.2) -> VideoClip:
        """
        Emotional scene - slow zoom + brightness increase
        
        Args:
            clip: Image/video clip
            zoom_amount: Amount to zoom (0.2 = 20%)
        """
        duration = clip.duration
        
        def scale_func(t):
            progress = t / duration
            scale = 1.0 + (zoom_amount * progress)
            return scale
        
        zoomed = clip.resize(scale_func)
        
        # Gradually increase brightness
        def brightness_func(t):
            progress = t / duration
            factor = 1.0 + (0.2 * progress)  # Up to 20% brighter
            return factor
        
        def brightness_filter(get_frame, t):
            frame = get_frame(t)
            factor = brightness_func(t)
            return np.clip(frame * factor, 0, 255).astype('uint8')
        
        return zoomed.fl(brightness_filter)
    
    @staticmethod
    def walk_slide(clip: VideoClip) -> VideoClip:
        """
        Walking scene - diagonal movement
        """
        duration = clip.duration
        
        def pos_func(t):
            progress = t / duration
            x = -150 + (300 * progress)  # Horizontal
            y = -50 + (100 * progress)   # Slight vertical
            return (x, y)
        
        return clip.set_position(pos_func)
    
    @staticmethod
    def dramatic_zoom(clip: VideoClip, zoom_ratio: float = 0.25) -> VideoClip:
        """
        Dramatic scene - fast zoom in
        
        Args:
            clip: Image/video clip
            zoom_ratio: Zoom ratio (0.25 = 25% zoom)
        """
        duration = clip.duration
        
        def scale_func(t):
            progress = t / duration
            # Ease-in effect (accelerating zoom)
            eased_progress = progress ** 2
            scale = 1.0 + (zoom_ratio * eased_progress)
            return scale
        
        return clip.resize(scale_func)


class VideoEffectsService:
    """
    Unified service for applying video effects and transitions
    """
    
    def __init__(self):
        self.transitions = VideoTransitions()
        self.effects = VideoEffects()
        self.presets = AnimationPresets()
    
    def apply_transition(
        self,
        clip: VideoClip,
        transition_type: str = "fade",
        duration: float = 0.5,
        **kwargs
    ) -> VideoClip:
        """
        Apply transition to clip
        
        Args:
            clip: Video clip
            transition_type: "fade", "slide", "zoom_in", "zoom_out"
            duration: Transition duration
            **kwargs: Additional transition-specific parameters
        
        Returns:
            Clip with transition applied
        """
        logger.info(
            "applying_transition",
            transition_type=transition_type,
            duration=duration
        )
        
        if transition_type == "fade":
            return self.transitions.fade_in(clip, duration)
        elif transition_type == "slide":
            direction = kwargs.get("direction", "left")
            return self.transitions.slide_in(clip, duration, direction)
        elif transition_type == "zoom_in":
            return self.transitions.zoom_in(clip)
        elif transition_type == "zoom_out":
            return self.transitions.zoom_out(clip)
        else:
            logger.warning(f"Unknown transition: {transition_type}, using fade")
            return self.transitions.fade_in(clip, duration)
    
    def apply_animation_preset(
        self,
        clip: VideoClip,
        preset: str = "talking_head",
        **kwargs
    ) -> VideoClip:
        """
        Apply animation preset
        
        Args:
            clip: Video clip
            preset: "talking_head", "action_pan", "emotion_pulse", "walk_slide", "dramatic_zoom"
            **kwargs: Preset-specific parameters
        
        Returns:
            Animated clip
        """
        logger.info("applying_animation_preset", preset=preset)
        
        if preset == "talking_head":
            return self.presets.talking_head(clip, **kwargs)
        elif preset == "action_pan":
            return self.presets.action_pan(clip, **kwargs)
        elif preset == "emotion_pulse":
            return self.presets.emotion_pulse(clip, **kwargs)
        elif preset == "walk_slide":
            return self.presets.walk_slide(clip)
        elif preset == "dramatic_zoom":
            return self.presets.dramatic_zoom(clip, **kwargs)
        else:
            logger.warning(f"Unknown preset: {preset}, using talking_head")
            return self.presets.talking_head(clip)
    
    def apply_effect(
        self,
        clip: VideoClip,
        effect_type: str,
        **kwargs
    ) -> VideoClip:
        """
        Apply visual effect
        
        Args:
            clip: Video clip
            effect_type: "brightness", "blur", "vignette", "color_temp"
            **kwargs: Effect-specific parameters
        
        Returns:
            Clip with effect applied
        """
        logger.info("applying_effect", effect_type=effect_type)
        
        if effect_type == "brightness":
            factor = kwargs.get("factor", 1.2)
            return self.effects.brightness(clip, factor)
        elif effect_type == "blur":
            radius = kwargs.get("blur_radius", 5)
            return self.effects.blur(clip, radius)
        elif effect_type == "vignette":
            intensity = kwargs.get("intensity", 0.5)
            return self.effects.vignette(clip, intensity)
        elif effect_type == "color_temp":
            temperature = kwargs.get("temperature", 1.0)
            return self.effects.color_temperature(clip, temperature)
        else:
            logger.warning(f"Unknown effect: {effect_type}")
            return clip


# Helper functions
def apply_random_animation(clip: VideoClip) -> VideoClip:
    """Apply random animation preset to clip"""
    import random
    
    presets = [
        ("talking_head", {}),
        ("action_pan", {"distance": 300}),
        ("emotion_pulse", {"zoom_amount": 0.2}),
        ("walk_slide", {}),
        ("dramatic_zoom", {"zoom_ratio": 0.25})
    ]
    
    preset_name, kwargs = random.choice(presets)
    service = VideoEffectsService()
    
    return service.apply_animation_preset(clip, preset_name, **kwargs)
