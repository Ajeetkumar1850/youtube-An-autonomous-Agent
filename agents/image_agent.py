import requests, urllib.parse ,time ,os
def generate_image(prompt, filename):
    # Enhanced prompt for animated look with character movements
    enhanced_prompt = f"{prompt}, character in motion, animated pose, expressive face with emotion, dynamic action"
    # Encode prompt properly
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    # Using enhanced model for better animation quality
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&enhance=true&nologo=true"
    print(f"   Generating {filename}...")

    try:
        response = requests.get(url, timeout=90)

        if response.status_code == 200:

            filepath = f"scenes/{filename}"
            
            # Create scenes folder if it doesn't exist
            os.makedirs("scenes", exist_ok=True)
            
            with open(filepath, "wb") as file:
                file.write(response.content)

            file_size = os.path.getsize(filepath)
            print(f"   ✓ {filename} generated! ({file_size} bytes)")
            
            # Delay to avoid rate limiting
            time.sleep(3)
            
            return filepath

        else:

            print(f"   ✗ Error: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None