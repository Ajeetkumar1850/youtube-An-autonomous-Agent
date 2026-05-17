import ollama

def generate_seo(topic, script):

    prompt = f"""
    You are a professional YouTube SEO expert.

    Based on this topic and script:

    Topic:
    {topic}

    Script:
    {script}

    Generate:

    1. Viral YouTube title
    2. SEO optimized description
    3. 10 hashtags
    4. 10 SEO tags

    Keep everything optimized for:
    - high CTR
    - YouTube Shorts
    - discoverability
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