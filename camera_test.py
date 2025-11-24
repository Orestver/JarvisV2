import cv2, playsound, requests
import pandas as pd
import google.generativeai as genai
import pyttsx3
import tempfile
import os
import asyncio
from dotenv import load_dotenv
from weather_forecast import WeatherForecast
from Jarvis_vosk import command_req, resource_path


async def handle_weather(command: str) -> dict | None:

    df = pd.read_excel('utils/worldcities.xlsx')
    city_list_lower = [c.lower() for c in df['city'].dropna().unique()]

    words = command.lower().split()
    weather = WeatherForecast()

    for word in words:
        if word in city_list_lower:
            weather_data = await weather.get_weather(word)
            return weather_data  # ❗ ТЕПЕР ПОВЕРТАЄМО ПОГОДУ

    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Can i get your location to get the weather Sir.mp3"))
    confirm = command_req().lower()

    if 'yes' in confirm or 'sure' in confirm:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        weather_data = await weather.get_weather(data['city'])
        return weather_data

    return None

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def analyze():
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    # Camera capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Камеру не знайдено!")

    print("🎥 Camera is running press'c', to take a picture and analize.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camera", frame)

        
        if cv2.waitKey(1) & 0xFF == ord('c'):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                cv2.imwrite(tmpfile.name, frame)

                weather_info = asyncio.run(handle_weather("What is the weather lviv"))
            
                if weather_info:
                    weather_text = str(weather_info)
                else:
                    weather_text = "unknown"

                response = model.generate_content([
                    f"Опиши людину на цьому фото..."
                    f"Чи можна так йти на двір якщо там така погода: {weather_text}",
                    {"mime_type": "image/jpeg", "data": open(tmpfile.name, "rb").read()}
                ])

                description = response.text
                print("\nAnalizyng...:", description)

            

    cap.release()
    cv2.destroyAllWindows()


analyze()