from agents.image_agent import generate_image
from agents.upload_agent import upload_video
from agents.video_agent import create_video
from agents.research_agent import research_topics
from agents.script_agent import generate_script
from agents.voice_agent import generate_voice
from agents.scene_agent import generate_scene_prompts
from agents.seo_agent import generate_seo
from agents.thumbnail_agent import generate_thumbnail_prompt

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
# GENERATE SCENE PROMPTS
# =========================

print("\nGenerating Scene Prompts...\n")

scene_text = generate_scene_prompts(script)

print(scene_text)

# Convert AI response into list
scene_prompts = scene_text.split("\n")

# =========================
# GENERATE SCENE IMAGES
# =========================

print("\nGenerating Scene Images...\n")

for i, prompt in enumerate(scene_prompts[:4]):

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
# GENERATE SEO
# =========================

print("\nGenerating SEO Metadata...\n")

seo_data = generate_seo(first_topic, script)

print(seo_data)

# Save SEO
with open("seo.txt", "w", encoding="utf-8") as file:
    file.write(seo_data)

# =========================
# GENERATE THUMBNAIL
# =========================

print("\nGenerating Thumbnail Prompt...\n")

thumbnail_prompt = generate_thumbnail_prompt(
    first_topic,
    script
)

print(thumbnail_prompt)

# Generate Thumbnail Image
generate_image(
    thumbnail_prompt,
    "thumbnail.png"
)

print("\nThumbnail generated successfully!")

# =========================
# UPLOAD VIDEO
# =========================

print("\nUploading to YouTube...\n")

upload_video()

print("\nPipeline Completed Successfully!")