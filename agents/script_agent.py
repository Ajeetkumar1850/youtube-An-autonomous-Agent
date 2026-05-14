import ollama

def generate_script(topic):

    prompt = f"""
    You are a professional YouTube Shorts script writer.

    Create a highly engaging 60-second YouTube Shorts script about:

    {topic}

    Requirements:
    - Strong hook in first 3 seconds
    - Simple language
    - Fast paced
    - Educational + engaging
    - Add ending call-to-action

    Format:
    Hook:
    Main Content:
    CTA:
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