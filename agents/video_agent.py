from moviepy.editor import *
import os

def create_video():

    # =====================================
    # CREATE VIDEOS FOLDER
    # =====================================

    os.makedirs("videos", exist_ok=True)

    # =====================================
    # LOAD AUDIO
    # =====================================

    audio = AudioFileClip("audio/output.wav")

    # =====================================
    # SCENE FILES
    # =====================================

    scene_files = [
        "scenes/scene1.png",
        "scenes/scene2.png",
        "scenes/scene3.png",
        "scenes/scene4.png"
    ]

    # =====================================
    # CALCULATE SCENE DURATION
    # =====================================

    duration_per_scene = audio.duration / len(scene_files)

    clips = []

    # =====================================
    # CREATE IMAGE CLIPS
    # =====================================

    for scene in scene_files:

        clip = (
            ImageClip(scene)
            .set_duration(duration_per_scene)
            .resize(height=1920)
            .set_position("center")
            .fadein(0.3)
            .fadeout(0.3)
        )

        clips.append(clip)

    # =====================================
    # COMBINE VIDEO CLIPS
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
    # EXPORT VIDEO
    # =====================================

    output_path = "videos/final_video.mp4"

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    print("\nVideo created successfully!")

    return output_path