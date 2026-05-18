import edge_tts
import asyncio
import os

# =====================================
# VOICE CONFIGURATION
# =====================================

VOICE = "hi-IN-SwaraNeural"

# Other good voices:
# hi-IN-MadhurNeural
# en-US-JennyNeural
# en-US-AriaNeural

# =====================================
# TEXT TO SPEECH FUNCTION
# =====================================

async def text_to_speech(text, output_file):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+10%"
    )

    await communicate.save(output_file)

# =====================================
# MAIN VOICE GENERATION FUNCTION
# =====================================

def generate_voice(script):

    # Create audio folder if missing
    os.makedirs("audio", exist_ok=True)

    output_file = "audio/output.mp3"

    # =====================================
    # CLEAN AI GENERATED TEXT
    # =====================================

    cleaned_script = script.replace("*", "")
    cleaned_script = cleaned_script.replace("#", "")
    cleaned_script = cleaned_script.replace("_", "")
    cleaned_script = cleaned_script.replace("**", "")
    cleaned_script = cleaned_script.replace("\n", " ")

    # Remove extra spaces
    cleaned_script = " ".join(cleaned_script.split())

    # =====================================
    # GENERATE VOICE
    # =====================================

    asyncio.run(
        text_to_speech(
            cleaned_script,
            output_file
        )
    )

    print("\nVoice generated successfully!")

    return output_file