import ollama

def generate_seo(topic, script):

    prompt = f"""
    You are a professional YouTube SEO expert.

    Generate SEO metadata for this YouTube Shorts video.

    Topic:
    {topic}

    Script:
    {script}

    STRICT FORMAT:

    TITLE:
    (one viral clickable title only)

    DESCRIPTION:
    (2 short engaging lines)

    HASHTAGS:
    (10 hashtags in one line)

    TAGS:
    (10 comma-separated SEO tags)

    Rules:
    - No explanations
    - No extra text
    - No markdown
    - No numbering
    - Keep title short and viral
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