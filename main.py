from agents.upload_agent import upload_video
from agents.video_agent import create_video
from agents.research_agent import research_topics
from agents.script_agent import generate_script
from agents.voice_agent import generate_voice

niche = input("Enter niche: ")

# Research Topics
results = research_topics(niche)

print("\nTrending Topics:\n")
print(results)

with open("topics.txt", "w", encoding="utf-8") as file:
    file.write(results)

# Select First Topic
first_topic = results.split("\n")[0]

print("\nGenerating Script...\n")

# Generate Script
script = generate_script(first_topic)

print(script)

with open("youtube_script.txt", "w", encoding="utf-8") as file:
    file.write(script)

# Generate Voice
print("\nGenerating Voice...\n")

audio_path = generate_voice(script)

#  generate video
print(f"Voice saved at: {audio_path}")
print("\nCreating Video...\n")

video_path = create_video(script)

print(f"\nVideo saved at: {video_path}")

#uploding part
print("\nUploading to YouTube...\n")

upload_video()