from agents.image_agent import generate_image
from agents.upload_agent import upload_video
from agents.video_agent import create_video
from agents.research_agent import research_topics
from agents.script_agent import generate_script
from agents.voice_agent import generate_voice

# User Input
niche = input("Enter niche: ")

# =========================
# RESEARCH TOPICS
# =========================

print("\nResearching Topics...\n")

results = research_topics(niche)

print("\nTrending Topics:\n")
print(results)

# Save Topics
with open("topics.txt", "w", encoding="utf-8") as file:
    file.write(results)

# =========================
# SELECT FIRST TOPIC
# =========================

first_topic = results.split("\n")[0]

# =========================
# GENERATE SCRIPT
# =========================

print("\nGenerating Script...\n")

script = generate_script(first_topic)

print(script)

# Save Script
with open("youtube_script.txt", "w", encoding="utf-8") as file:
    file.write(script)

# =========================
# GENERATE SCENE IMAGES
# =========================

print("\nGenerating Scene Images...\n")

scene_prompts = [
    "cute cartoon dog playing in park, animated style",
    "cartoon dog sleeping on sofa, cinematic lighting",
    "cartoon dog running in garden, vibrant colors",
    "cute emotional cartoon dog with owner"
]

for i, prompt in enumerate(scene_prompts):

    filename = f"scene{i+1}.png"

    generate_image(prompt, filename)

# =========================
# GENERATE VOICE
# =========================

print("\nGenerating Voice...\n")

audio_path = generate_voice(script)

print(f"\nVoice saved at: {audio_path}")

# =========================
# CREATE VIDEO
# =========================

print("\nCreating Video...\n")

video_path = create_video()

print(f"\nVideo saved at: {video_path}")

# =========================
# UPLOAD VIDEO
# =========================

print("\nUploading to YouTube...\n")

upload_video()

print("\nPipeline Completed Successfully!")