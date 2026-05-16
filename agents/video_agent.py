from moviepy.editor import *

def create_video():

    # Load audio
    audio = AudioFileClip("audio/output.mp3")

    # Scene files
    scene_files = [
        "scenes/scene1.png",
        "scenes/scene2.png",
        "scenes/scene3.png",
        "scenes/scene4.png"
    ]

    # Duration per scene
    duration_per_scene = audio.duration / len(scene_files)

    clips = []

    for scene in scene_files:

        clip = ImageClip(scene)

        clip = clip.set_duration(duration_per_scene)

        clips.append(clip)

    # Combine scenes
    video = concatenate_videoclips(
        clips,
        method="compose"
    )

    # Add audio
    video = video.set_audio(audio)

    # Export
    output_path = "videos/final_video.mp4"

    video.write_videofile(
        output_path,
        fps=24
    )

    return output_path