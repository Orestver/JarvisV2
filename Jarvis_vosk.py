import asyncio, wikipedia
import concurrent.futures
import random, json
import pyttsx3
from datetime import datetime, timedelta
import datetime, time
import os, sys
import functools
import pandas as pd
import re
import threading
import winsound
import unidecode 
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import speech_recognition as sr
from google import genai
from google.genai import types
import webbrowser
import urllib.parse
import subprocess
import psutil
import pygetwindow as gw
from pywinauto.application import Application
import requests
import yt_dlp # для відкриття відео на ю тубі | for opening videos on youtube
from PIL import Image
from io import BytesIO
import ctypes, winshell
from pathlib import Path
import playsound
import vosk
import sounddevice as sd
import queue
import json

import keyboard # для очікування натискання клавіші | for waiting  break key press



from weather_forecast import WeatherForecast
from memory_manager import AssistantMemory
from news_handler import get_latest_news
from parse_films import search_and_open_film
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
memory = AssistantMemory()
#change if plan in elevemlabs is over
#from speak import speak # <-----------------------Change here
from elevenlabsspeach import speak  #<------------ Change here
#from main import speak

MODEL_PATH = "vosk-model-small-en-us-0.15" 
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000
DEVICE_ID = None

q = queue.Queue()
vosk_model = vosk.Model(MODEL_PATH)

stop_command_listening = False


standard_responses_for_questions = [
    "Loading... Sir",
    "Processing...",
    "Just a moment, Sir.",
    "Let me think about that, Sir.",
    "I'm on it, Sir.",
    "Give me a second, Boss."
]
# для .exe версії
def resource_path(relative_path) -> str:
    try:
        base_path = sys._MEIPASS  # коли запаковано в .exe
    except AttributeError:
        base_path = os.path.abspath(".")  # коли просто скрипт
    return os.path.join(base_path, relative_path)

def extract_voice_command(folder_path="Jarvis_voice_commands/standart_responses") -> list:
# Отримаємо список всіх mp3-файлів у папці
    audio_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith(".mp3")
    ]
    return audio_files



# Function to save text to PDF
def save_to_pdf(text: str) -> Path:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        downloads_path = Path.home() / "Downloads"
        filename = downloads_path / f"travel_plan_{now}.pdf"
        c = canvas.Canvas(str(filename), pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('DejaVuSans', 'utils/DejaVuSans.ttf'))
        c.setFont("DejaVuSans", 12)

        left_margin = 40
        right_margin = 40
        top_margin = 40
        bottom_margin = 40
        line_height = 18
        max_width = width - left_margin - right_margin

        text_object = c.beginText(left_margin, height - top_margin)
        text_object.setFont("DejaVuSans", 12)

        for paragraph in text.split('\n'):
            words = paragraph.split()
            line = ""

            for word in words:
                test_line = line + " " + word if line else word
                if pdfmetrics.stringWidth(test_line, "DejaVuSans", 12) < max_width:
                    line = test_line
                else:
                    if text_object.getY() <= bottom_margin:
                        c.drawText(text_object)
                        c.showPage()
                        c.setFont("DejaVuSans", 12)
                        text_object = c.beginText(left_margin, height - top_margin)
                        text_object.setFont("DejaVuSans", 12)
                    text_object.textLine(line)
                    line = word

            if line:
                if text_object.getY() <= bottom_margin:
                    c.drawText(text_object)
                    c.showPage()
                    c.setFont("DejaVuSans", 12)
                    text_object = c.beginText(left_margin, height - top_margin)
                    text_object.setFont("DejaVuSans", 12)
                text_object.textLine(line)

            text_object.textLine("")

        c.drawText(text_object)
        c.save()
        print(f"Your travel plan has been saved to {filename}")
        return filename

# Function to save music to json file
def save_musics_json() -> None:
    import json
    with open('musics.json', 'w') as file:
        json.dump(musics, file, indent=4)
    print("Music list saved to musics.json.")

# Function to listen for user command
def command_req() -> str | None:
    global stop_command_listening
    if stop_command_listening:
        return None

    rec = vosk.KaldiRecognizer(vosk_model, SAMPLE_RATE)
    rec.SetWords(True)
    partial_text = ""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        device=DEVICE_ID,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):
        print("\n🎤 Слухаю команду...")

        while True:
            if stop_command_listening:
                return None

            data = q.get()

            if stop_command_listening:
                return None

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"\nРозпізнано команду: {text}")
                    return text.lower()

            else:
                partial = json.loads(rec.PartialResult())
                current_partial = partial.get("partial", "")
                if current_partial != partial_text:
                    partial_text = current_partial
                    print(f"\r🎤 ...{partial_text}", end="", flush=True)

            if stop_command_listening:
                return None

# Audio callback function
def audio_callback(indata, frames, time, status) -> None:
    if status:
        print(status)
    q.put(bytes(indata))

# Function to wait for the wake word
def wait_for_command() -> str:
    rec = vosk.KaldiRecognizer(vosk_model, SAMPLE_RATE)
    rec.SetWords(True)
    partial_text = ""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        device=DEVICE_ID,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):
        print("🎧 Waiting for wake word 'jarvis' ")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower().strip()
                if text:
                    print(f"\nПочув: {text}")
                    if any(phrase in text for phrase in ["jarvis", "gandhi's", "got it is","jerry's","nervous","john with","gary's", "doris"]):
                        playsound.playsound("Jarvis_voice_commands/command_responses/Ready to help Sir.mp3")
                        wishMe() 
                        return "smth"  # return any non-empty string to indicate wake word detected
            else:
                partial = json.loads(rec.PartialResult())
                current_partial = partial.get("partial", "")
                if current_partial != partial_text:
                    partial_text = current_partial
                    print(f"\r🎤 ...{partial_text}", end="", flush=True)

# Function for keyboard listener to stop command listening
def keyboard_listener() -> None:
    global stop_command_listening
    # слухає глобально, незалежно від фокуса
    keyboard.add_hotkey('q', lambda: set_flag())

# Function to set the stop flag
def set_flag() -> None:
    global stop_command_listening
    print("Stopping command listening...")
    stop_command_listening = True

# Function for AI consultation
def consultation(command: str) -> None:




    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = (
        f"You're Jarvis, an AI voice assistant, speaking to the user in a natural, friendly tone. "
        f"Speak like you speak with human and i tell you: '{command}'. "
        "Dont use unicode characters, just use normal letters. "
        "Speak casually and clearly, like you're explaining something out loud to a person. "
        "Use contractions and natural language, as if you're talking in a normal conversation. "
        "Don't use greetings or closings, just start answering right away, and also dont give such a long answer, "
        "Avoid technical jargon unless necessary. Keep it short and helpful."
        "Dont give so long answers hust a few sentenses"
    )
    
    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
    response_text = response.text.strip()
    if response_text:
        speak(response_text)
        print(f"AI Response: {response_text}")
        print("✅ Response from AI received successfully.")
    else:
        speak("Sorry, I couldn't find an answer to your question. Please try again later or ask something else.")
        print("⚠️ No response from AI. Please try again later or ask something else.")


# Function to extract time from phrase
def extract_time_fast(phrase: str) -> str | None:
    phrase = phrase.lower()

    # 1️⃣ Якщо є число ("after 10 minutes")
    match = re.search(r"\d+", phrase)
    if match:
        number = int(match.group())
        for unit in ["seconds", "second", "minutes", "minute", "hours", "hour"]:
            if unit in phrase:
                return f"{number} {unit}"
        return str(number)

    # 2️⃣ Якщо число словами
    number_words = {
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"
    }
    hours_words = {"seconds", "second", "minutes", "minute", "hours", "hour"}

    words = phrase.replace('-', ' ').split()
    buffer = []
    time_unit = None

    for word in words:
        if word in number_words:
            buffer.append(word)
        elif word in hours_words:
            time_unit = word
        elif buffer:
            break  # зупиняємось, коли пройшли числа

    if buffer:
        try:
            number_unit = words_to_number(' '.join(buffer))
        except Exception:
            return None
        if time_unit:
            return f"{number_unit} {time_unit}"
        return str(number_unit)

    return None

# Function for opening YouTube video
def open_youtube_video(query: str):
    if not query:
        print("❌ Немає назви пісні для пошуку")
        return

    print(f"🔎 Шукаю '{query}'...")
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = f"https://www.youtube.com/watch?v={info['id']}"
        print(f"🎬 Відкриваю: {info['title']}")
        webbrowser.open(url)

# Function to extract song name from phrase
def extract_song_name(phrase: str) -> str | None:
    phrase = phrase.lower()
    trigger_words = ["play", "song", "music", "track"]


    #r'\b(play|song|music|track)\b'
    # \b - межа слова на початку і в кінці щоб бралося лише повне слово play а не частина іншого наприклад display

    match = re.search(r'\b(' + '|'.join(trigger_words) + r')\b', phrase)
    if match:
        # Беремо все після trigger слова як назву пісні
        song_name = phrase[match.end():].strip()
        # Прибираємо зайві слова типу 'please', 'for me'
        song_name = re.sub(r'\b(for me|please|now|place|police)\b', '', song_name).strip()
        print("Extracted song name:", song_name)
        return song_name
    return None

# Function to extract number from phrase
def extract_number_fast(phrase: str) -> int | None:
    phrase = phrase.lower()
    
    match = re.search(r"\d+", phrase)
    if match:
        return int(match.group())

    number_words = {
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"
    }

    words = phrase.replace('-', ' ').split()
    buffer = []

    for word in words:
        if word in number_words:
            buffer.append(word)
        elif buffer:
            return words_to_number(' '.join(buffer))

    if buffer:
        return words_to_number(' '.join(buffer))
    
    return None

# Function to generate travel prompt
def generate_prompt(command: str) -> str | None:
    playsound.playsound(resource_path('Jarvis_voice_commands/command_responses/Generating travel plan based on your command..mp3'))
    #speak("Generating travel plan based on your command.")
    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = ("Ok i have this prompt: "
            "You are a caring and knowledgeable travel planning assistant with an outgoing and funny personality. "
            "My name is {name}. I am planning to travel to {destination} in {style} style "
            "for {days} days. "
            "Write the response in {language} language. "
            "Describe what to do each day in detail and give some advices."
            "Edit this prompt depends on the command: "
            f"{command}. "
            "And return just the prompt, nothing else."
            "And if i dont give all data just remove this dat from the prompt"
            "All the variables in the prompt must be filled"
            "If name not given set it to traveler"
            "And if language in not given set in to english"
            "And if number of days is not given set it to 3 or 5 days")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    prompt_text = response.text.strip()
    if prompt_text:
        print(f"Generated Prompt: {prompt_text}")
        return prompt_text

# Function to create travel plan for user
def create_plan(text_prompt: str) -> str:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = text_prompt

    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
    plan_text = response.text
    plan_text = unidecode.unidecode(plan_text)  # Remove unicode characters
    save_to_pdf(plan_text)
    #speak("Your travel plan has been created successfully.")
    playsound.playsound(resource_path('Jarvis_voice_commands/command_responses/Your travel plan has been created successfully.mp3'))
    return plan_text
    
# Function to check current time and day
def check_time() -> None:
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    weekday_index = now.weekday()  # 0–6
    days = {
        0: "Monday", 
        1: "Tuesday", 
        2: "Wednesday", 
        3: "Thursday", 
        4: "Friday", 
        5: "Saturday", 
        6: "Sunday"
    }

    current_day = days[weekday_index]
    print(f"The time is: {current_time}, and today is: {current_day}")
    speak(f"The time is: {current_time}, and today is: {current_day}")

# Function to wish user based on time of day
def wishMe() -> None:
    hour = datetime.datetime.now().hour
    wishes = extract_voice_command('Jarvis_voice_commands/greetings')
    if hour >= 0 and hour < 12:
        playsound.playsound(wishes[2])
    elif hour >= 12 and hour < 18:
        playsound.playsound(wishes[0])
    else:
        playsound.playsound(wishes[1])

# Function for volume control
def volume_control(command: str) -> None:
    volume = extract_number_fast(command)
    if not volume:
        print('Add e percents of what you want to set the volume')
        return
    try:
        if 0 <= volume <= 100:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(
                        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                    volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)
                    speak(f"Volume set to {volume} percent.")
        else:
                    speak("Please enter a valid number between 0 and 100.")
    except ValueError:
            speak("Invalid input. Please enter a number between 0 and 100.")

# Function for mute control
def mute_control(command: str) -> None:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
    if 'mute' in command:
        speak("Muting the system.")
        print("Muting the system.")
    elif 'unmute' in command:
        speak("Unmuting the system.")
        print("Unmuting the system.")
    if volume_control.GetMute():
        volume_control.SetMute(0, None)
        speak("Unmuted.")
    else:
        volume_control.SetMute(1, None)
        speak("Muted.")

# Function to open websites or applications
def opener(command: str) -> None:
    if 'youtube' in command or 'ютуб' in command:
        #speak("Opening YouTube.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening YouTube..mp3"))
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/What do you want to watch on YouTube.mp3"))
        #speak("What do you want to watch on YouTube?")
        query = command_req()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        speak(f"Searching for {query} on YouTube.")
        webbrowser.open(url)

    elif 'google' in command or 'гугл' in command:
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Google..mp3"))
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/What do you want to search.mp3"))
        #speak("Opening Google.")
        #speak("What do you want to search.")
        query = command_req()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        speak(f"Searching for {query} on Google.")
        webbrowser.open(url)

    elif 'telegram' in command or 'телеграм' in command:
        #speak("Opening Telegram.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Telegram..mp3"))
        os.system("start https://web.telegram.org")

    elif 'github' in command or 'гітхаб' in command:
        #speak("Opening GitHub.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening GitHub..mp3"))
        os.system("start https://github.com")
    elif 'instagram' in command or 'інстаграм' in command:
        #speak("Opening Instagram.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Instagram..mp3"))
        os.system("start https://www.instagram.com")
    elif 'discord' in command or 'діскорд' in command:
        #speak("Opening Discord.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Discord..mp3"))
        os.system("start https://discord.com/app")
    else:
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Maybe you want something else Please specify..mp3"))
        #speak("Maybe you want something else? Please specify.")

# Function to handle file creation
def filehandle() -> None:
    #peak("What file do you want to create? PDF, TXT, or DOCX?")
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/What file do you want to create. PDF, TXT, or DOCX.mp3"))
    type = input("Enter file type (pdf/docx/txt): ").strip().lower()
    #speak("Please enter the name of the file you want to create.")
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Please enter the name of the file you want to create..mp3"))
    filename = input("Enter file name: ").strip()

    if 'pdf' in type:
        filename += '.pdf'
        speak(f"Creating PDF file named {filename}.")
    if 'docx' in type:
        filename += '.docx'
        speak(f"Creating DOCX file named {filename}.")
    if 'txt' in type or not filename:
        filename += '.txt'
        speak(f"Creating TXT file named {filename}.")
    if not filename.endswith(('.pdf', '.docx', '.txt')):
        #speak("Invalid file type. Please try again.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Invalid file type. Please try again..mp3"))
        print("⚠️ Invalid file type. Please try again.")
        return
    try:
        with open(filename, 'w') as file:
            speak(f"File {filename} created successfully.")
            print(f"File {filename} created successfully.")
            #speak("Do you want to write something in this file?")
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Do you want to write something in this file..mp3"))
            command = command_req().strip().lower()
            if 'yes' in command or 'так' in command:
                os.system(f"start {filename}")
                #speak("You can write in the file now.")
                playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/You can write in the file now..mp3"))
            else:
                #speak("File created without any content.")
                playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/File created without any content..mp3"))
                print("File created without any content.")

    except Exception as e:
        speak(f"An error occurred while creating the file: {e}")
        print(f"⚠️ Error: {e}")

# Function for opening applications
def aps(command: str) -> None:

    if 'calculator' in command or 'калькулятор' in command:
        #speak("Opening Calculator.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Calculator..mp3"))
        os.system("start calc")
    elif 'notepad' in command or 'блокнот' in command:
        #speak("Opening Notepad.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Notepad..mp3"))
        os.system("start notepad")
    elif 'docs' in command or 'документи' in command:
        #speak("Opening Documents.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Documents..mp3"))
        webbrowser.open("https://docs.google.com/document/u/0/")
    else:
        #speak("I don't know this application. Please try again.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/I don't know this application. Please try again..mp3"))

# Function to run games with volume adjustment
def runner(command: str) -> None:
    #speak("Please specify the application you want to run.")
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Please specify the application you want to run..mp3"))
    app_name = command_req().strip().lower()
    if 'gothic' in app_name or 'gothic 3' in app_name or 'gothic' in command or 'gothic 3' in command:
        #speak("Opening Gothic 3.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Gothic 3..mp3"))
        exe_path = r"D:/Gothic 3/Gothic3.exe"
        working_dir = r"D:/Gothic 3"
        subprocess.Popen(exe_path, cwd=working_dir)
        #speak("Gothic 3 is now running.")
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Gothic 3 is now running..mp3"))
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Do you want to lower the volume to 20%.mp3"))
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Volume set to 20%..mp3"))
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Enjoy your game.mp3"))

    elif 'cs2' in app_name or 'counter strike 2' in app_name or 'cs2' in command or 'counter strike 2' in command:
        #speak("Opening Counter-Strike 2.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Counter-Strike 2..mp3"))
        subprocess.Popen(r'start steam://run/730', shell=True)
        #speak("Do you want to lower the volume to 70%?")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Do you want to lower the volume to 70%.mp3"))
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.7, None)
            #speak("Volume set to 70%.")
            #speak("Enjoy your game!")
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Volume set to 70%..mp3"))
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Enjoy your game.mp3"))

    elif 'titan' in app_name or 'titan' in command or 'quest' in app_name or 'quest' in command:
        #speak("Opening Titan Quest.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Titan Quest..mp3"))
        subprocess.Popen(r'start steam://run/475150', shell=True)
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Do you want to lower the volume to 20%.mp3"))
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Volume set to 20%..mp3"))
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Enjoy your game.mp3"))
    elif 'terraria' in app_name or 'terraria' in command:
        #speak("Opening Terraria.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Opening Terraria..mp3"))
        subprocess.Popen(r'start steam://run/105600', shell=True)
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Do you want to lower the volume to 20%.mp3"))
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Volume set to 20%..mp3"))
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Enjoy your game.mp3"))
    else:
        #peak("I don't know this application. Please try again.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/I don't know this application. Please try again..mp3"))
        print("⚠️ I don't know this application. Please try again.")
        return

# Function for checking system information
def sysinfo() -> None:
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    batery = psutil.sensors_battery()
    charge = batery.percent if batery else "N/A"
    total_memory = memory_info.total / (1024 ** 3)  # Convert to GB
    used_memory = memory_info.used / (1024 ** 3)  # Convert to GB
    free_memory = memory_info.free / (1024 ** 3)  # Convert to GB
    speak(f"Battery charge is {charge} percent. CPU usage is {cpu_usage} percent. Free memory is {free_memory:.2f} gigabytes.")

    print(f"Battery charge: {charge}%")
    print(f"CPU Usage: {cpu_usage}%")
    print(f"Free Memory: {free_memory:.2f} GB")

# Function to play random music from the list --------change the musics.json file to add musict or use add_music function--------
def play_music() -> None:
    with open('musics.json', 'r') as file:
        import json
        global musics
        musics = json.load(file)
    url = random.choice(list(musics.values()))
    webbrowser.open(url)
    

# Function to add music to the list in musics.json
def add_music() -> None:
    #speak("Please enter the name of the song you want to add.")
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Please enter the name of the song you want to add..mp3"))
    song_name = input("Enter song name: ").strip().lower() 
    #speak("Please enter the YouTube link for the song.")
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Please enter the YouTube link for the song..mp3"))
    song_link = input("Enter YouTube link: ").strip()
    
    if song_name and song_link:
        musics[song_name] = song_link
        save_musics_json()
        speak(f"Song '{song_name}' added successfully.")
        print(f"Song '{song_name}' added successfully.")
    else:
        #speak("Invalid input. Please try again.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Invalid input. Please try again..mp3"))
        print("⚠️ Invalid input. Please try again.")

# Function to roll up (minimize) all Chrome windows
def roll_up() -> None:
    # Використовуємо .visible замість .isVisible
    chrome_windows = [w for w in gw.getWindowsWithTitle('Chrome') if w.visible]

    for win in chrome_windows:
        try:
            app = Application().connect(handle=win._hWnd)
            app_window = app.window(handle=win._hWnd)
            app_window.minimize()
        except Exception as e:
            print(f"Не вдалося згорнути: {e}")

# Function to extract time from phrase quickly
def extract_time_fast(phrase: str) -> str | None:
    phrase = phrase.lower()

    #IF number ("after 10 minutes")
    match = re.search(r"\d+", phrase)
    if match:
        number = int(match.group())
        for unit in ["seconds", "second", "minutes", "minute", "hours", "hour"]:
            if unit in phrase:
                return f"{number} {unit}"
        return str(number)
    
    #IF number in words
    number_words = {
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"
    }
    hours_words = {"seconds", "second", "minutes", "minute", "hours", "hour"}

    words = phrase.replace('-', ' ').split()
    buffer = []
    time_unit = None

    for word in words:
        if word in number_words:
            buffer.append(word)
        elif word in hours_words:
            time_unit = word
        elif buffer:
            break  # stop when passed numbers

    if buffer:
        try:
            number_unit = words_to_number(' '.join(buffer))
        except Exception:
            return None
        if time_unit:
            return f"{number_unit} {time_unit}"
        return str(number_unit)

    return None

# Function to convert time and set timer
def convert_time(sentence: str) -> None:
    match = re.search(r'\d+', sentence)
    if not match:
        print('Invalid input')
        return
    time = int(match.group())
    if 'hour'in sentence or 'hours' in sentence:
        seconds = time*3600
        speak(f'The timer set to {seconds} hours')
    elif 'minute'in sentence or 'minutes' in sentence:
        seconds = time*60
        speak(f'The timer set to {seconds} minutes')

    elif 'second'in sentence or 'seconds' in sentence:
        seconds = time
        speak(f'The timer set to {seconds} seconds')
    else:
        print('Invalid time format please try hour, minutes, or seconds')
    try:
        threading.Thread(target=set_timer, args=(seconds,), daemon=True).start()
    except Exception as e:
        print(f'An error occured {e}')

# Function to set timer
def set_timer(amount: int) -> None:
    time.sleep(amount)
    print("⏰ Час вийшов!")

    # Звук (тільки для Windows)
    try:
        winsound.Beep(1000,1000)
        #speak('Beep!!, Beep!!, Timer is out STAND UP!')
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Beep!!, Beep!!, Timer is out STAND UP!.mp3"))  # частота 1000Гц, тривалість 1 сек
    except:
        print("🔔 Дзвінок!")

# Function to get weather information
async def handle_weather(command: str) -> dict | None:

    df = pd.read_excel('utils/worldcities.xlsx')  # Файл з бази SimpleMaps
    city_list = df['city'].dropna().unique().tolist()
    city_list_lower = [c.lower() for c in city_list]
    words = command.split()
    weather = WeatherForecast()
    for word in words:
        if word in city_list_lower:
            await weather.get_weather(word)
            return
    #speak('Can i get your location to get the weather Sir?')
    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Can i get your location to get the weather Sir.mp3"))
    confirm = command_req().lower()
    if 'yes' in confirm or 'sure' in confirm:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        await weather.get_weather(data['city'])
        return {
             "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc")  # широта, довгота
        }
    elif 'no' in confirm:
        #speak('Ok than enter the city where you want to get weather')
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Ok than enter the city where you want to get weather.mp3"))

# Function to set the alarm clock
def set_alarm(target_time: datetime.time) -> None:
    while True:
        now = datetime.datetime.now().time()
        if now.hour == target_time.hour and now.minute == target_time.minute:
            #speak('ALARM, ALARM, the clock is out. You must to go to do something')
            playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/ALARM, ALARM, the clock is out. You must to go to do something.mp3"))
            break  # інакше буде нескінченний спам
        time.sleep(1)  # затримка, щоб не навантажувати процесор



# Function to convert words to numbers
def words_to_number(text) -> int | None:
    num_words = {
        "zero": 0,"one": 1,"two": 2,"three": 3,"four": 4,"five": 5,"six": 6,"seven": 7,"eight": 8,"nine": 9,"ten": 10,"eleven": 11,"twelve": 12,
        "thirteen": 13,"fourteen": 14,"fifteen": 15,"sixteen": 16,"seventeen": 17,"eighteen": 18,"nineteen": 19,"twenty": 20,"thirty": 30,"forty": 40,
        "fifty": 50,"sixty": 60,"seventy": 70,"eighty": 80,"ninety": 90,
    }

    multipliers = {
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000
    }
    text = text.lower().replace("-", " ")
    words = text.split()

    total = 0
    current = 0
    
    for w in words:
        if w in num_words:
            current += num_words[w]
        elif w in multipliers:
            if current == 0:
                current = 1
            current *= multipliers[w]
            total += current
            current = 0
        else:
            return None  
    return total + current


# Function to extract time for alarm clock
def extract_time(text) -> str | None:
    num_words = {
        "zero": 0,"one": 1,"two": 2,"three": 3,"four": 4,"five": 5,"six": 6,"seven": 7,"eight": 8,"nine": 9,"ten": 10,"eleven": 11,"twelve": 12,
        "thirteen": 13,"fourteen": 14,"fifteen": 15,"sixteen": 16,"seventeen": 17,"eighteen": 18,"nineteen": 19,"twenty": 20,"thirty": 30,"forty": 40,
        "fifty": 50,"sixty": 60,"seventy": 70,"eighty": 80,"ninety": 90,
    }

    multipliers = {
        "hundred": 100,
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000
    }
    text = text.lower()

    # 1. if already in numbers 12.30 or 12:30
    match = re.search(r"(\d{1,2})[.:](\d{1,2})", text)
    if match:
        hh, mm = match.groups()
        return f"{int(hh):02d}:{int(mm):02d}"

    # if in words
    words = text.split()

    number_words = []
    for w in words:
        if w in num_words or w in multipliers:
            number_words.append(w)

    if not number_words:
        return None

    #if only houres
    if len(number_words) == 1:
        hh = words_to_number(number_words[0])
        return f"{hh:02d}:00"

    if len(number_words) >= 2:
        hh = words_to_number(number_words[0])
        mm = words_to_number(" ".join(number_words[1:]))
        return f"{hh:02d}:{mm:02d}"

    return None


# Function to set alarm clock
def set_alarm_clock(command: str) -> None:
    match = re.search(r'\b(?:[0-1]?\d|2[0-3]):(?:[0-5]\d)\b', command)
    if not match:
        print('Invalid input')
        return

    time_str = match.group()  # "11:45"
    alarm_time = str_to_time(time_str)

    speak(f'The alarm clock is set to {alarm_time.hour}:{alarm_time.minute:02d}')
    print(f'The alarm clock is set to {alarm_time.hour}:{alarm_time.minute:02d}')
    try:
        threading.Thread(target=set_alarm, args=(alarm_time,), daemon=True).start()
    except Exception as e:
        print(f'Error with thread: {e}')

# Function to convert str to time 
def str_to_time(time_str: str) -> datetime.time:
    hour, minute = map(int, time_str.split(":"))
    return datetime.time(hour, minute)

# Functin to generate image using Gemini API ----Curently not working due to API issues----            
def gen_image(command: str) -> None:
    match = re.search(r'(image|about|where|like|)\s+(.+)', command)
    if match:
        result = match.group(2)
        client = genai.Client(api_key=GOOGLE_API_KEY)
        prompt = result
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=2

            )
        )
        for i in enumerate(response.generated_images):
            image = Image.open(BytesIO(image.image.image_bytes))
            image.save(f'gemini-native-image-{i}.png')
            image.show()

            upscale_factor = 4
            upscaled_image = image.resize((image.width * upscale_factor, image.height * upscale_factor), resample=Image.LANCZ05)
            upscaled_image.save(f'{result}-{i}.png')
            upscaled_image.show()

    elif not match:
        speak('Oops something went wrong try again with generate image and your prompt')

# Function to search and open film
def open_film(command: str) -> None:
    match = re.search(r'(open|watch|see|turn on)\s+(.+)', command)
    if match:
        result = match.group(2)
        print(result)
        search_and_open_film(result)
        #speak("Enjoy your watching")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Enjoy your watching.mp3"))
    else:
        #speak('Something went wrong try again')
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Something went wrong try again.mp3"))

# Function to get all the user`s meetings`
def get_meeting_list(lang='en') -> str:
    meetings = memory.get_meetings()
    if not meetings:
        return "You have no scheduled meetings." if lang == 'en' else "У вас немає запланованих зустрічей."
    
    lines = ["Your meetings:" if lang == 'en' else "Ваші зустрічі:"]
    for m in meetings:
        lines.append(f"- {m['date']} at {m['time']}: {m['topic']}")
    return "\n".join(lines)

# Function to claer all meetings
def clear_meetings_command(command: str) -> str | None:
    if "clear" in command or "очисти" in command:
        memory.clear_meetings()
        return "All meetings have been cleared."
    return None

# Function to parse meeting details from command
def parse_meeting(command: str) -> dict | None:
    command = command.lower()

    # патерн: підтримка "10:00 p.m.", "10 p.m.", "tomorrow", "for ..."
    # pattern like "add meeting at 10:30 a.m. tomorrow for project discussion"
    pattern = r"(add|schedule|create|запиши|додай|створи)\s+(meeting|зустріч)\s+(at|на)?\s*(\d{1,2})([:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?\s*(today|tomorrow|завтра|сьогодні)?\s*(for|щоб)?\s*(.*)"
    match = re.search(pattern, command)

    if not match:
        return None 

    # ----------Groups------------
    # 4 — hours
    # 6 — minutes (group included in 5)
    # 7 — am/pm
    # 8 — date (today/tomorrow)
    # 10 — topic

    hour = int(match.group(4))
    minute = int(match.group(6)) if match.group(6) else 0
    meridiem = match.group(7)
    date_word = match.group(8)
    topic = match.group(10).strip() if match.group(10) else "no topic"

    # AM/PM обробка
    if meridiem and 'p' in meridiem and hour < 12:
        hour += 12
    elif meridiem and 'a' in meridiem and hour == 12:
        hour = 0

    # Дата
    today = datetime.datetime.now()
    if date_word in ['tomorrow', 'завтра']:
        date = today + timedelta(days=1)
    elif date_word in ['today', 'сьогодні']:
        date = today
    else:
        date = today  # за замовчуванням — сьогодні

    return {
        "date": date.strftime("%Y-%m-%d"),
        "time": f"{hour:02}:{minute:02}",
        "topic": topic
    }

# Function to check meetings and return reminders
def check_meetings(json_file: str='memory.json', minutes_before: int=60) -> list:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    now = datetime.datetime.now()
    reminders = []

    for meeting in data.get("meetings", []):
        try:
            meeting_datetime = datetime.datetime.strptime(f"{meeting['date']} {meeting['time']}", "%Y-%m-%d %H:%M")
            time_diff = meeting_datetime - now

            if datetime.timedelta(0) <= time_diff <= datetime.timedelta(minutes=minutes_before):
                topic = meeting.get("topic", "no topic")
                # Ідентифікатор зустрічі — можна використовувати дату+час+тему
                meeting_id = f"{meeting['date']} {meeting['time']} {topic}"
                reminders.append({
                    "id": meeting_id,
                    "time_str": meeting_datetime.strftime('%H:%M'),
                    "topic": topic
                })
        except Exception as e:
            print(f"⚠️ Помилка в записі зустрічі: {e}")
            continue

    return reminders

# Function that runs reminder loop for meetings
def reminder_loop() -> None:
    already_reminded = {}  # dict: meeting_id -> last_reminder_time (datetime)

    REMINDER_INTERVAL = datetime.timedelta(minutes=5)  # мінімальний інтервал між нагадуваннями
    CHECK_INTERVAL = 30  # секунд між перевірками

    while True:
        now = datetime.datetime.now()
        reminders = check_meetings()

        for reminder in reminders:
            meeting_id = reminder["id"]
            last_time = already_reminded.get(meeting_id)

            # Якщо ще не нагадували або минуло більше 10 хв з останнього нагадування
            if last_time is None or (now - last_time) > REMINDER_INTERVAL:
                speak(f"Boss, you have a meeting at {reminder['time_str']}: {reminder['topic']}")
                already_reminded[meeting_id] = now

        time.sleep(CHECK_INTERVAL)

# Function to check battery status periodically
def check_battery() -> None:
    while True:
        time.sleep(300)  # Check every 5 minutes ---You can change the time interval here---
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged
            if percent < 30 and not plugged:

                speak("Warning! Battery is below 30 percent. Please connect to a power source.")
                
            elif percent == 100 and plugged:
                speak("Battery is fully charged. You can unplug the charger.")
            
# Function to search Wikipedia and return short summary
def search_wikipedia(query: str) -> str:
    try:
        wikipedia.set_lang("en")  # або "en" для англійської
        summary = wikipedia.summary(query, sentences=2)  # 2 речення
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Занадто багато значень: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Сторінку не знайдено."
    except Exception as e:
        return f"Сталася помилка: {e}"

# Function to empty the recycle bin
def empty_recycle_bin() -> None:
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        print("Recycle Bin cleared.")
        #speak("The recycle bin has been cleared.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/The recycle bin has been cleared..mp3"))
    except Exception as e:
        print(f"Failed to clear: {e}")

# Function to get installed Steam games ---Currently only works on Windows and with exceptions---
def get_installed_steam_games() -> list:
    steam_path = r"C:\\Program Files (x86)\\Steam\\steamapps\\common"
    if not os.path.exists(steam_path):
        return []

    games = [name for name in os.listdir(steam_path)
             if os.path.isdir(os.path.join(steam_path, name))]
    return games


# Functiom to run the specified game
def launch_game(game_name: str) -> None:
    steam_games = get_installed_steam_games()
    matched_games = [g for g in steam_games if game_name.lower() in g.lower()]

    if not matched_games:
        print(f"Гру '{game_name}' не знайдено серед встановлених.")
        return

    game_folder = matched_games[0]
    game_path = os.path.join(r"C:\Program Files (x86)\Steam\steamapps\common", game_folder)

    # Шукаємо .exe файл у папці гри (простий варіант)
    for root, dirs, files in os.walk(game_path):
        for file in files:
            if file.endswith(".exe") and game_folder.lower() in file.lower():
                full_path = os.path.join(root, file)
                print(f"Запуск: {full_path}")
                subprocess.Popen(full_path)
                return

    print(f"Не знайдено .exe файл для гри '{game_folder}'")

# Function to extract game name from command
def extract_game_name(command: str) -> str | None:
    match = re.search(r"(play|грати)\s+(.*)", command)
    if match:
        return match.group(2).strip()
    return None




# Function to take a screenshot
def take_the_screenshot() -> str:
    import pyautogui, os
    from datetime import datetime
    from PIL import ImageEnhance

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)

    # Make screenshot
    screenshot = pyautogui.screenshot()

    # Slightly enchance image
    sharp = ImageEnhance.Sharpness(screenshot).enhance(1.5)
    contrast = ImageEnhance.Contrast(sharp).enhance(1.1)

    # Save file with high quality
    filename = f"{folder}/screenshot_{timestamp}.png"
    contrast.save(filename, quality=95)
    return filename

# Main async function to run the voice assistant and handle all commands
async def run_voice_assistant() -> None:
    global stop_command_listening
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        threading.Thread(target=reminder_loop, daemon=True).start()
        threading.Thread(target=check_battery, daemon=True).start()

        threading.Thread(target=keyboard_listener, daemon=True).start()
        while True:
            command = await loop.run_in_executor(executor, wait_for_command)
            if not command:
                continue
            stop_command_listening = False
            while True:
                print("🎤 Listening for command press 'q' to quit...")
                if stop_command_listening:
                    break

                command = await loop.run_in_executor(executor, command_req)
                action_performed = False
                if not command:
                    continue
                standart_responses = extract_voice_command()
                rand_standart_responses = random.choice(standart_responses)
                await loop.run_in_executor(executor, playsound.playsound, rand_standart_responses)
                
                if any(x in command for x in ['what is the time', 'час', 'date', 'дата']):
                    await loop.run_in_executor(executor, check_time)
                    action_performed = True

                if 'volume' in command or 'гучність' in command:
                    await loop.run_in_executor(executor, volume_control, command)
                    action_performed = True

                if any(x in command for x in ['mute', 'unmute', 'вимкнути', 'увімкнути']):
                    await loop.run_in_executor(executor, mute_control, command)
                    action_performed = True

                if any(x in command for x in ['youtube', 'ютуб', 'google', 'гугл', 'telegram', 'телеграм', 'github', 'гітхаб']):
                    await loop.run_in_executor(executor, opener, command)
                    action_performed = True

                if 'thanks' in command or 'thank you' in command:
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/You're welcome! If you need anything else, just ask..mp3")
                    action_performed = True

                if 'create file' in command or 'створити файл' in command:
                    await loop.run_in_executor(executor, filehandle)
                    action_performed = True


                if 'take screenshot' in command or 'take the screenshot' in command or 'take a screenshot' in command:
                    
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Taking a screenshot..mp3")
                    await loop.run_in_executor(executor, take_the_screenshot)
                    action_performed = True

                if any(x in command for x in ['calculator', 'калькулятор', 'notepad', 'блокнот', 'docs', 'документи','documents']):
                    await loop.run_in_executor(executor, aps, command)
                    action_performed = True

                if 'clear' in command or 'очистити' in command:
                    #await loop.run_in_executor(executor, speak, "Clearing the console.")
                    await loop.run_in_executor(executor, playsound.playsound,"Jarvis_voice_commands/command_responses/Clearing the console..mp3")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    action_performed = True

                if 'run' in command or 'запустити' in command:
                    await loop.run_in_executor(executor, runner, command)
                    action_performed = True

                if any(x in command for x in ['check', 'system', 'система']):    
                    #await loop.run_in_executor(executor, speak, "Checking system information.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Checking system information..mp3")
                    await loop.run_in_executor(executor, sysinfo)
                    action_performed = True

                if any(x in command for x in ['play the music', 'музику', 'listen music', 'слухати музику', 'play the song', 'пісню','слухати', 'play a song', 'play a music', 'play some music', 'play']):                   
                    #await loop.run_in_executor(executor, speak, "Playing a random song from your playlist.")
                    #await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Playing a random song from your playlist..mp3")
                    if 'play the music' in command or 'listen music' in command or 'when the music' in command:
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Playing a random song from your playlist..mp3")
                        await loop.run_in_executor(executor, play_music)
                        time.sleep(3)
                        await loop.run_in_executor(executor, roll_up)
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Enjoy your music.mp3")
                        action_performed = True
                    else:
                        song_name = await loop.run_in_executor(executor, extract_song_name, command)
                        await loop.run_in_executor(executor, open_youtube_video, song_name)
                        time.sleep(3)
                        await loop.run_in_executor(executor, roll_up)
                        #await loop.run_in_executor(executor, speak, "Enjoy your music")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Enjoy your music.mp3")
                        action_performed = True

                if 'add song' in command or 'додати музику' in command:                   
                    await loop.run_in_executor(executor, add_music)
                    action_performed = True

                if 'shutdown' in command or 'вимкнути' in command:
                    #await loop.run_in_executor(executor, speak, "Are you sure you want to shut down the system? Say 'yes' or 'no'.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Are you sure you want to shut down the system Say 'yes' or 'no'..mp3")
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        #await loop.run_in_executor(executor, speak, "Shutting down the system.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Shutting down the system..mp3")
                        os.system("shutdown /s /t 1")
                    else:
                        #await loop.run_in_executor(executor, speak, "Shutdown cancelled.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Shutdown cancelled..mp3")
                    action_performed = True

                if 'latest news' in command:
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Searching for latest news....mp3")
                    news_list = await loop.run_in_executor(executor, get_latest_news)
                    for n in news_list:
                        print("🔹", n["title"])
                        print("   📅", n["published"])
                        print("   🔗", n["url"])
                        print()
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Here is the list of 10 latest news..mp3")
                    action_performed = True

                if 'restart' in command or 'перезавантажити' in command:
                    #await loop.run_in_executor(executor, speak, "Are you sure you want to restart the system? Say 'yes' or 'no'.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Are you sure you want to restart the system Say 'yes' or 'no'..mp3")
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        await loop.run_in_executor(executor, speak, "Restarting the system.")
                        os.system("shutdown /r /t 1")
                    else:
                        await loop.run_in_executor(executor, speak, "Restart cancelled.")
                    action_performed = True

                if 'weather' in command or 'погода' in command:
                    await handle_weather(command)
                    action_performed = True


                if 'route' in command or 'маршрут' in command or 'destination' in command or 'road' in command  :
                    #await loop.run_in_executor(executor, speak, "Please enter the destination address.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Please enter the destination address..mp3")
                    destination = input("Enter destination address: ").strip()
                    if destination:
                        url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination)}"
                        webbrowser.open(url)
                        await loop.run_in_executor(executor, speak, f"Opening route to {destination} on Google Maps.")
                    else:
                       #await loop.run_in_executor(executor, speak, "Invalid destination address. Please try again.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Invalid destination address. Please try again..mp3")
                    action_performed = True


                if any(x in command for x in ['travel plan', 'план подорожі', 'create travel plan', 'подорож', 'Journay']):
                    create_plan_prompt = await loop.run_in_executor(executor, generate_prompt, command)
                    await loop.run_in_executor(executor, create_plan, create_plan_prompt)
                    action_performed = True

                if 'roll up' in command or 'згорнути' in command:
                    await loop.run_in_executor(executor, roll_up)
                    action_performed = True

                if 'timer' in command or 'set the timer' in command:
                    command = extract_time_fast(command)               
                    await loop.run_in_executor(executor, convert_time, command)
                    action_performed = True

                if 'alarm clock' in command or 'set the clock' in command:
                    time_str  = await loop.run_in_executor(executor,extract_time, command)
                    await loop.run_in_executor(executor,set_alarm_clock, time_str)
                    action_performed = True

                #need paid status   
                if 'generate image' in command or 'create image' in command:
                    await loop.run_in_executor(executor, gen_image,command)
                    action_performed = True

                if 'watch' in command  or 'turn on' in command:
                    await loop.run_in_executor(executor, open_film, command)
                    action_performed = True

                if 'who i am' in command or 'who am i' in command or 'what is my name' in command:
                    name = memory.recall("name")
                    if name:
                        await loop.run_in_executor(executor, speak, f"Of cource you are {name}.")
                    else:
                        #await loop.run_in_executor(executor, speak, "I don't know your name yet. Please tell me your name first.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/I don't know your name yet. Please tell me your name first..mp3")
                    action_performed = True

                elif 'i am a' in command or 'my name is' in command or 'my name' in command:
                    match = re.search(r'(i am|i am a|my name is|my name)\s+(.+)', command)
                    if match:
                        name = match.group(2)
                        memory.remember("name", name)
                        print(f"Remember: {name}")
                    else:
                        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/I didn't catch your name. Please try again..mp3"))
                        print("I didn't catch your name. Please try again.")
                    action_performed = True

                if any(trigger in command for trigger in ["schedule meeting", "запиши зустріч", "add meeting", 'add meetings', 'add a meeting']):
                    meeting = parse_meeting(command)
                    if meeting:
                        memory.add_meeting(meeting["date"], meeting["time"], meeting["topic"])
                        await loop.run_in_executor(executor, speak, f"Meeting at {meeting['time']} on {meeting['date']} saved: {meeting['topic']}")
                    else:
                        #await loop.run_in_executor(executor, speak, "I didn't understand the meeting time or format.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/I didn't understand the meeting time or format..mp3")
                    action_performed = True

                if any(trig in command for trig in ['show meetings', 'what meetings', 'які зустрічі', 'покажи зустрічі','meetings','what meetings do i have','show my meetings']):
                    lang = 'en' if 'what' in command or 'show' in command else 'ua'
                    result = get_meeting_list(lang)

                    await loop.run_in_executor(executor, speak, result)
                    await loop.run_in_executor(executor, print, result)
                    action_performed = True

                if "clear meetings" in command or "очисти зустрічі" in command or 'clear the meetings' in command or 'delete meetings' in command:
                    result = clear_meetings_command(command)
                    if result:
                        await loop.run_in_executor(executor, speak, result)
                        action_performed = True

                if 'close browser' in command or 'закрити браузер' in command or 'close the browser' in command or 'close google' in command:
                    #speak('Closing all browser windows.')
                    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Closing all browser windows..mp3"))
                    os.system('taskkill /f /im chrome.exe')  # Замість chrome.exe можна використовувати інший браузер
                    action_performed = True

                if 'clear the bin' in command or 'clear bin' in command or 'очисти кошик' in command:
                    await loop.run_in_executor(executor, empty_recycle_bin)
                    await loop.run_in_executor(executor, speak, "The recycle bin has been cleared")
                    action_performed = True

                if 'wikipedia' in command or 'вікіпедія' in command:
                    playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/What do you want to search on Wikipedia.mp3"))
                    query = await loop.run_in_executor(executor, command_req)
                    if query:
                        result = search_wikipedia(query)
                        await loop.run_in_executor(executor, speak, result)
                        await loop.run_in_executor(executor, print, result)
                        action_performed = True
                    else:
                        #await loop.run_in_executor(executor, speak, "I didn't catch your query. Please try again.")
                        await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/I didn't catch your query. Please try again..mp3")
                        print("I didn't catch your query. Please try again.")
                        action_performed = True
                """    
                if "play" in command or "грати" in command:
                    game_name = extract_game_name(command)
                    if game_name:
                        launch_game(game_name)
                    else:
                        await loop.run_in_executor(executor, speak, "I didn't understand the game name. Please try again.")
                        print("I didn't understand the game name. Please try again.")
                    action_performed = True
                    """
                if any(x in command for x in ['exit', 'вихід', 'turn off', 'bye']):
                    #await loop.run_in_executor(executor, speak, "Goodbye! Have a great day!")
                    await loop.run_in_executor(executor, playsound.playsound, 'Jarvis_voice_commands/command_responses/Goodbye! Have a great day!.mp3')
                    action_performed = True
                    break
                if not action_performed:
                    if any(x in command for x in ['?', 'what', 'who', 'how', 'why']):
                        standart_responses = extract_voice_command()
                        rand_standart_responses = random.choice(standart_responses)
                        await loop.run_in_executor(executor, playsound.playsound, rand_standart_responses)
                        await loop.run_in_executor(executor, consultation, command)
                    else:
                        await loop.run_in_executor(executor, consultation, command)

# Run the voice assistant
if __name__ == "__main__":
    asyncio.run(run_voice_assistant())
