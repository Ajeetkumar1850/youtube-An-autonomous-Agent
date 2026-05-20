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
    # CREATE DYNAMIC SHOT CLIPS
    # =====================================

    for image in image_files:

        clip = (
            ImageClip(image)
            .set_duration(duration_per_shot)
            .resize(height=1920)
            .set_position("center")
        )

        # =====================================
        # RANDOM ZOOM EFFECT
        # =====================================

        zoom_in = random.choice([True, False])

        if zoom_in:

            clip = clip.resize(
                lambda t: 1 + 0.04 * t
            )

        else:

            clip = clip.resize(
                lambda t: 1 - 0.03 * t
                if 1 - 0.03 * t > 0.7
                else 0.7
            )

        # =====================================
        # RANDOM PAN EFFECT
        # =====================================

        direction = random.choice(
            ["left", "right", "up", "down", "none"]
        )

        if direction != "none":

            def move(t):

                x, y = 0, 0

                if direction == "left":
                    x = -40 * t

                elif direction == "right":
                    x = 40 * t

                elif direction == "up":
                    y = -30 * t

                elif direction == "down":
                    y = 30 * t

                return (x, y)

            clip = clip.set_position(move)

        # =====================================
        # SMOOTH TRANSITIONS
        # =====================================

        clip = clip.fadein(0.2).fadeout(0.2)

        clips.append(clip)

    # =====================================
    # COMBINE ALL SHOTS
    # =====================================

    video = concatenate_videoclips(
        clips,
        method="compose"
    )

    # =====================================
    # ADD AUDIO
    # =====================================

    video = video.set_audio(audio)

    # =====================================
    # EXPORT FINAL VIDEO
    # =====================================

    output_path = "videos/final_video.mp4"

    video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )

    print("\nDynamic video created successfully!")

    return output_path