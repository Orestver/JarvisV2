import requests,os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")


url = "https://api.elevenlabs.io/v1/user/subscription"

headers = {
    "xi-api-key": API_KEY
}

response = requests.get(url, headers=headers)

print(response.json())
