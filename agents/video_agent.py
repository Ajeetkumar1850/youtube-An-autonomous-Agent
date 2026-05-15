from moviepy.editor import *

def create_video(script):

    # Load audio
    audio = AudioFileClip("audio/output.mp3")

    # Load background image
    image = ImageClip("assets/bg.jpg")

    # Match duration with audio
    image = image.set_duration(audio.duration)

    # Add audio
    video = image.set_audio(audio)

    # Output path
    output_path = "videos/final_video.mp4"

    # Export video
    video.write_videofile(
        output_path,
        fps=24
    )

    return output_path