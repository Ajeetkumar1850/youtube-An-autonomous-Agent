from gtts import gTTS
def generate_voice(script):
    tts = gTTS(
        text=script,
        lang='en',
        slow=False
    )
    output_file = "audio/output.mp3"
    tts.save(output_file)
    return output_file