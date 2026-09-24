from moviepy.editor import *
import os
import random

def create_video(image_files):

    # =====================================
    # CREATE VIDEOS FOLDER
    # =====================================

    os.makedirs("videos", exist_ok=True)

    # =====================================
    # LOAD AUDIO
    # =====================================

    audio = AudioFileClip("audio/output.wav")

    # =====================================
    # CALCULATE SHOT DURATION
    # =====================================

    duration_per_shot = audio.duration / len(image_files)

    clips = []

    # =====================================
    # CREATE ANIMATED CLIPS
    # =====================================

    for i, image in enumerate(image_files):

        # =====================================
        # BASE CLIP
        # =====================================

        clip = (
            ImageClip(image)
            .set_duration(duration_per_shot)
            .resize(height=1920)
        )

        # =====================================
        # ANIMATION STYLES (YouTube-like)
        # =====================================

        animation = random.choice([
            "talking_zoom",      # For speaking scenes
            "action_pan",        # For movement scenes
            "emotion_pulse",     # For emotional moments
            "walk_slide",        # For walking scenes
            "dramatic_zoom"      # For dramatic moments
        ])

        # =====================================
        # TALKING ZOOM (Mouth Movement Effect)
        # =====================================

        if animation == "talking_zoom":
            
            # Subtle zoom in/out to simulate talking
            clip = clip.resize(
                lambda t: 1.05 + 0.03 * (t % 0.5)  # Quick pulse effect
            )

        # =====================================
        # ACTION PAN (Hand/Body Movement)
        # =====================================

        elif animation == "action_pan":
            
            clip = clip.resize(1.15)
            
            # Horizontal movement
            clip = clip.set_position(
                lambda t: (
                    -100 + (t / duration_per_shot) * 200,
                    "center"
                )
            )

        # =====================================
        # EMOTION PULSE (Eye Expression Effect)
        # =====================================

        elif animation == "emotion_pulse":
            
            # Slow zoom for emotional impact
            clip = clip.resize(
                lambda t: 1 + 0.2 * (t / duration_per_shot)
            )
            
            # Slight brightness change for emotion
            clip = clip.fx(vfx.colorx, 1.15)

        # =====================================
        # WALK SLIDE (Foot Movement Effect)
        # =====================================

        elif animation == "walk_slide":
            
            clip = clip.resize(1.2)
            
            # Diagonal movement to simulate walking
            clip = clip.set_position(
                lambda t: (
                    -(t / duration_per_shot) * 150,
                    50 - (t / duration_per_shot) * 100
                )
            )

        # =====================================
        # DRAMATIC ZOOM (Full Character Focus)
        # =====================================

        elif animation == "dramatic_zoom":
            
            # Fast zoom in
            clip = clip.resize(
                lambda t: 1 + 0.25 * (t / duration_per_shot)
            )

        # =====================================
        # SMOOTH TRANSITIONS
        # =====================================

        clip = clip.fadein(0.3).fadeout(0.3)

        # =====================================
        # RANDOM BRIGHTNESS FOR VARIETY
        # =====================================

        if i % 4 == 0:
            clip = clip.fx(vfx.colorx, 1.1)

        clips.append(clip)

    # =====================================
    # COMBINE ALL CLIPS
    # =====================================

    video = concatenate_videoclips(clips, method="compose")

    # =====================================
    # ADD AUDIO
    # =====================================

    video = video.set_audio(audio)

    # =====================================
    # EXPORT (OPTIMIZED FOR LOW CPU)
    # =====================================

    output_path = "videos/final_video.mp4"

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2,
        bitrate="2500k"
    )

    print("\n✓ Animated video created successfully!")

    return output_path