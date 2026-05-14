from agents.research_agent import research_topics
from agents.script_agent import generate_script

niche = input("Enter niche: ")

# Generate topics
results = research_topics(niche)

print("\nTrending Topics:\n")
print(results)

# Save topics
with open("topics.txt", "w", encoding="utf-8") as file:
    file.write(results)

# Select first topic
first_topic = results.split("\n")[0]

print("\nGenerating Script For:")
print(first_topic)

# Generate script
script = generate_script(first_topic)

print("\nGenerated Script:\n")
print(script)

# Save script
with open("youtube_script.txt", "w", encoding="utf-8") as file:
    file.write(script)

print("\nScript saved successfully!")