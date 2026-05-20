from agents.image_agent import generate_image
from agents.upload_agent import upload_video
from agents.video_agent import create_video
from agents.research_agent import research_topics
from agents.script_agent import generate_script
from agents.voice_agent import generate_voice
from agents.shot_agent import generate_shots
from agents.seo_agent import generate_seo

# =========================
# USER INPUT
# =========================

niche = input("Enter niche: ")

# =========================
# RESEARCH TOPICS
# =========================

print("\nResearching Topics...\n")

results = research_topics(niche)

print("\nTrending Topics:\n")
print(results)

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

with open("youtube_script.txt", "w", encoding="utf-8") as file:
    file.write(script)

# =========================
# GENERATE CINEMATIC SHOTS
# =========================

print("\nGenerating Cinematic Shots...\n")

shots = generate_shots(script)

for shot in shots:

    print(shot)

# =========================
# GENERATE SHOT IMAGES
# =========================

print("\nGenerating Shot Images...\n")

image_files = []

for i, shot in enumerate(shots[:12]):

    filename = f"scene{i+1}.png"

    generate_image(shot, filename)

    image_files.append(
        f"scenes/{filename}"
    )

# =========================
# GENERATE VOICE
# =========================

print("\nGenerating Voice...\n")

audio_path = generate_voice(script)

print(f"\nVoice saved at: {audio_path}")

# =========================
# CREATE DYNAMIC VIDEO
# =========================

print("\nCreating Dynamic Video...\n")

video_path = create_video(image_files)

print(f"\nVideo saved at: {video_path}")

# =========================
# GENERATE SEO
# =========================

print("\nGenerating SEO Metadata...\n")

seo_data = generate_seo(first_topic, script)

print(seo_data)

with open("seo.txt", "w", encoding="utf-8") as file:
    file.write(seo_data)

# =========================
# UPLOAD VIDEO
# =========================

print("\nUploading to YouTube...\n")

upload_video()

print("\nPipeline Completed Successfully!")