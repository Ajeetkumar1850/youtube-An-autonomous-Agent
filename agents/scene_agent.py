import ollama

def generate_scene_prompts(script):

    prompt = f"""
    Read this YouTube Shorts script carefully.

    Generate 4 cinematic animated scene prompts.

    Rules:
    - Cartoon style
    - Visually detailed
    - Colorful
    - Short prompts
    - Each scene should match the story progression
    - Make scenes feel dynamic and engaging

    Script:
    {script}

    Return ONLY the prompts.
    One prompt per line.
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