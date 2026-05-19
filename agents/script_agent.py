import ollama

def generate_script(topic):

    prompt = f"""
    You are a professional Hindi YouTube Shorts storyteller.

    Create a SHORT emotional storytelling script in Hindi.

    Topic:
    {topic}

    IMPORTANT RULES:
    - Write ONLY in Hindi
    - Make it sound like a real storyteller
    - Conversational tone
    - Emotional narration
    - Cartoon storytelling style
    - Simple Hindi words
    - Add curiosity
    - Add drama
    - Add emotions
    - Add natural pauses

    VERY IMPORTANT:
    - No numbering
    - No bullet points
    - No headings
    - No markdown
    - No labels like Hook/CTA
    - No English
    - No emojis

    The script should feel like:
    - animated story narration
    - kids storytelling
    - cartoon YouTube Shorts

    Keep script around 45–60 seconds.
    """

    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return response['message']['content'].strip()