import ollama

def generate_shots(script):

    prompt = f"""
    You are a professional animated movie storyboard artist.

    Read the Hindi story carefully.

    Generate EXACTLY 12 cinematic animated shot prompts.

    IMPORTANT RULES:
    - One short shot per line
    - Focus only on visuals
    - Cartoon animation style
    - Disney Pixar style
    - Cute expressive characters
    - Emotional storytelling visuals
    - Camera angles allowed
    - Keep shots simple and easy for AI image generation
    - Short prompts only
    - No numbering
    - No explanations
    - No markdown
    - No extra text

    GOOD EXAMPLES:

close-up cartoon mother crying in bedroom

little boy standing in rain with umbrella

mother hugging child emotionally

wide shot of cartoon family walking together

sad child sitting alone in colorful room

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

    shot_text = response['message']['content'].strip()

    styled_shots = []

    for line in shot_text.split("\\n"):

        line = line.strip()

        if line:

            line += ", disney pixar cartoon style, colorful lighting, ultra detailed"

            styled_shots.append(line)

    return styled_shots