import ollama

def generate_thumbnail_prompt(topic, script):

    prompt = f"""
    You are a professional YouTube thumbnail designer.

    Create ONE cinematic thumbnail image prompt.

    Topic:
    {topic}

    Script:
    {script}

    Rules:
    - Highly clickable
    - Emotional
    - Bright colors
    - Cartoon animated style
    - Cinematic lighting
    - YouTube Shorts style
    - Short and detailed

    Return ONLY the image prompt.
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

    return response['message']['content']