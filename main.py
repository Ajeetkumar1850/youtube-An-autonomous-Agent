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

print(f"Voice saved at: {audio_path}")