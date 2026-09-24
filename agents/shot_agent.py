import ollama

def generate_shots(script):

    prompt = f"""
    You are a professional animated movie storyboard artist.

    Read the Hindi story carefully.

    Generate EXACTLY 12 cinematic animated shot prompts with CHARACTER ACTIONS.

    IMPORTANT RULES:
    - Describe character movements and expressions
    - Include: mouth movements, hand gestures, eye expressions, body language
    - Cartoon animation style
    - Disney Pixar style
    - Cute expressive characters
    - Emotional storytelling visuals
    - Action-focused descriptions
    - Keep shots simple
    - Short prompts only
    - No numbering
    - No explanations
    - No markdown

    GOOD EXAMPLES:

cartoon mother talking with mouth open, hands gesturing emotionally, tears in eyes

little boy walking with arms swinging, looking around curiously, expressive face

mother hugging child tightly, eyes closed, gentle smile, warm expression

cartoon family walking together, waving hands, laughing with open mouths

sad child sitting with head down, wiping tears, shoulders slumped

happy character jumping with arms raised, big smile, excited eyes

character speaking with animated mouth movements, pointing finger, surprised expression

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

    # Split by newlines
    lines = shot_text.split("\n")
    
    for line in lines:

        line = line.strip()
        
        # Remove numbering if present (1., 2., etc.)
        if line and len(line) > 3:
            
            # Remove leading numbers and dots
            import re
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^\*\*?\s*', '', line)  # Remove markdown
            line = re.sub(r'\*\*?\s*$', '', line)
            
            line = line.strip()

            if line:
                # Enhanced prompt for animation
                line += ", animated character with movement, disney pixar style, expressive animation, colorful lighting, ultra detailed, smooth motion"

                styled_shots.append(line)

    # Ensure we have at least 8 shots
    if len(styled_shots) < 8:
        print(f"Warning: Only {len(styled_shots)} shots generated. Adding default shots...")
        
        default_shots = [
            "cartoon character talking with mouth open, hands gesturing",
            "character walking with arms swinging, happy expression",
            "character with surprised face, eyes wide open, hands raised",
            "character smiling warmly, eyes closed, peaceful expression"
        ]
        
        while len(styled_shots) < 8:
            styled_shots.append(default_shots[len(styled_shots) % len(default_shots)] + ", animated character with movement, disney pixar style, expressive animation, colorful lighting, ultra detailed, smooth motion")

    return styled_shots