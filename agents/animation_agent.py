import requests, urllib.parse,  time ,os
def generate_animated_clip(prompt, output_filename, duration=3):
    """
    Generate animated video clip with character movements
    Using Pollinations AI video generation (FREE)
    """
    
    # Enhanced prompt for animation
    animation_prompt = f"{prompt}, animated character moving, talking with mouth movement, expressive eyes blinking, hand gestures, body language, smooth animation, cartoon style"
    
    encoded_prompt = urllib.parse.quote(animation_prompt)
    
    # Pollinations Video API (experimental)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&enhance=true"
    
    print(f"Generating animated clip: {output_filename}")
    
    try:
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            
            filepath = f"scenes/{output_filename}"
            
            with open(filepath, "wb") as file:
                file.write(response.content)
            
            print(f"✓ {output_filename} generated!")
            return filepath
            
        else:
            print(f"✗ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error generating animation: {e}")
        return None


# =====================================
# GENERATE MULTIPLE ANIMATED FRAMES
# For smoother animation effect
# =====================================

def generate_animation_frames(prompt, base_filename, num_frames=3):
    """
    Generate multiple frames with slight variations
    to create animation effect when played in sequence
    """
    
    frames = []
    
    variations = [
        "character with mouth open speaking",
        "character with eyes blinking, hand raised",
        "character with different expression, body turned"
    ]
    
    for i in range(num_frames):
        
        frame_prompt = f"{prompt}, {variations[i % len(variations)]}"
        
        filename = f"{base_filename}_frame{i+1}.png"
        
        frame_path = generate_animated_clip(frame_prompt, filename)
        
        if frame_path:
            frames.append(frame_path)
        
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    return frames
