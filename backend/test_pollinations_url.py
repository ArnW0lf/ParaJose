import urllib.parse
import os
import requests

def test_url_generation():
    prompt = "Modern tech interface, abstract lines, vibrant colors, high detail"
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true&seed={os.urandom(2).hex()}"
    
    print(f"Generated URL: {image_url}")
    
    try:
        response = requests.get(image_url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Image URL is valid and accessible.")
        else:
            print("Image URL returned an error.")
    except Exception as e:
        print(f"Error accessing URL: {e}")

if __name__ == "__main__":
    test_url_generation()
