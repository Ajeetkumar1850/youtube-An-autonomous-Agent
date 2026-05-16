import requests
import urllib.parse

def generate_image(prompt, filename):

    # Encode prompt properly
    encoded_prompt = urllib.parse.quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    response = requests.get(url)

    if response.status_code == 200:

        with open(f"scenes/{filename}", "wb") as file:
            file.write(response.content)

        print(f"{filename} generated successfully!")

    else:

        print("Error generating image")
        print(response.status_code)