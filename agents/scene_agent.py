import ollama

def generate_scene_prompts(script):

    prompt = f"""
    You are an AI storyboard artist.

    Read the Hindi story script carefully.

    Generate EXACTLY 4 short visual image prompts.

    IMPORTANT RULES:
    - Only visual descriptions
    - Cartoon animated style
    - Cute emotional characters
    - Bright colorful scenes
    - Disney Pixar style
    - Short prompts only
    - One line per scene
    - Focus on visible objects/actions
    - No emotions explanation
    - No story explanation
    - No cinematic analysis
    - No numbering
    - No markdown

    GOOD EXAMPLE:
    cute cartoon mother hugging little boy in colorful room

    Script:
    {script}
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

    scene_text = response['message']['content'].strip()

    # =====================================
    # ADD CONSISTENT VISUAL STYLE
    # =====================================

    styled_lines = []

    for line in scene_text.split("\n"):

        line = line.strip()

        if line:

            line += ", disney pixar cartoon style, colorful lighting, ultra detailed"

            styled_lines.append(line)

    return "\n".join(styled_lines)