import ollama

def generate_thumbnail_prompt(topic, script):

    prompt = f"""
    You are a professional YouTube thumbnail designer.

    Create ONE short cinematic thumbnail image prompt.

    Topic:
    {topic}

    Script:
    {script}

    Rules:
    - highly clickable
    - emotional expression
    - bright colors
    - cartoon animated style
    - cinematic lighting
    - short detailed prompt
    - visually dramatic

    IMPORTANT:
    - Return ONLY the image prompt
    - No headings
    - No explanations
    - No markdown
    - No extra text
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