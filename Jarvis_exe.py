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
from PIL import Image
from io import BytesIO
import ctypes, winshell
from pathlib import Path
import playsound
from weather_forecast import WeatherForecast
from memory_manager import AssistantMemory
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
memory = AssistantMemory()
#change if plan is over
#from speak import speak
from elevenlabsspeach import speak
#from main import speak

standard_responses_for_questions = [
    "Loading... Sir",
    "Processing...",
    "Just a moment, Sir.",
    "Let me think about that, Sir.",
    "I'm on it, Sir.",
    "Give me a second, Boss."
]
# для .exe версії
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # коли запаковано в .exe
    except AttributeError:
        base_path = os.path.abspath(".")  # коли просто скрипт
    return os.path.join(base_path, relative_path)

def extract_voice_command(folder_path="Jarvis_voice_commands/standart_responses"):
# Отримаємо список всіх mp3-файлів у папці
    audio_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith(".mp3")
    ]
    return audio_files


def save_to_pdf(text):
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

def save_musics_json():
    import json
    with open('musics.json', 'w') as file:
        json.dump(musics, file, indent=4)
    print("Music list saved to musics.json.")


def command_req():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Чутливість до гучності
    recognizer.dynamic_energy_threshold = True  # Автоматичне налаштування під шум
    recognizer.pause_threshold = 0.8  # Коротка пауза — кінець фрази
    recognizer.non_speaking_duration = 0.5  # Тиша до/після фрази
    recognizer.phrase_threshold = 0.3  # Мінімум для виявлення мовлення
    recognizer.operation_timeout = 10  # Максимальний час очікування запису

    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
    try:
        command_text = recognizer.recognize_google(audio, language='en-US')# ukrainian - uk-UA english - en-US
        print(f"Command recognized: {command_text}")
        return command_text.lower()
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""


def wait_for_command():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Чутливість до гучності
    recognizer.dynamic_energy_threshold = True  # Автоматичне налаштування під шум
    recognizer.pause_threshold = 0.8  # Коротка пауза — кінець фрази
    recognizer.non_speaking_duration = 0.5  # Тиша до/після фрази
    recognizer.phrase_threshold = 0.3  # Мінімум для виявлення мовлення
    recognizer.operation_timeout = 10  # Максимальний час очікування запису
    with sr.Microphone() as source:
        print("🎧 Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command_text = recognizer.recognize_google(audio, language='en-US') # ukrainian - uk-UA english - en-US
        print(f"🔊 Heard: {command_text}")

        if 'jarvis' in command_text.lower(): #джарвіс
            playsound.playsound(resource_path('Jarvis_voice_commands/command_responses/Ready to help Sir.mp3'))
            wishMe()  # ← Додаємо вітання тут
            return "smth"  # повертаємо пусто, щоб перейти у while-loop
        if 'віра' in command_text.lower():
            speak("Так сер")
            wishMe()  # ← Додаємо вітання тут
            return "smth"  # повертаємо пусто, щоб перейти у while-loop
        else:
            print("🔕 Wake word not detected.")
            return ""
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Could not request results: {e}")
        return ""


def consultation(command):




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


def generate_prompt(command):
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


def create_plan(text_prompt):
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
    

def check_time():
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


def wishMe():
    hour = datetime.datetime.now().hour
    wishes = extract_voice_command('Jarvis_voice_commands/greetings')
    if hour >= 0 and hour < 12:
        playsound.playsound(wishes[2])
    elif hour >= 12 and hour < 18:
        playsound.playsound(wishes[0])
    else:
        playsound.playsound(wishes[1])


def volume_control(command):
    match = re.search(r'\d+', command)
    if not match:
        print('Add e percents of what you want to set the volume')
        return
    try:
        volume = int(match.group())
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


def mute_control(command):
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


def opener(command):
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


def filehandle():
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


def aps(command):

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


def runner(command):
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


def sysinfo():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    batery = psutil.sensors_battery()
    charge = batery.percent if batery else "N/A"
    total_memory = memory_info.total / (1024 ** 3)  # Convert to GB
    used_memory = memory_info.used / (1024 ** 3)  # Convert to GB
    free_memory = memory_info.free / (1024 ** 3)  # Convert to GB
    speak(f"Battery charge: {charge}%")
    speak(f"CPU Usage: {cpu_usage}%")
    speak(f"Free Memory: {free_memory:.2f} GB")

    print(f"Battery charge: {charge}%")
    print(f"CPU Usage: {cpu_usage}%")
    print(f"Free Memory: {free_memory:.2f} GB")


def play_music():
    with open('musics.json', 'r') as file:
        import json
        global musics
        musics = json.load(file)
    url = random.choice(list(musics.values()))
    webbrowser.open(url)
    


def add_music():
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


def roll_up():
    # Використовуємо .visible замість .isVisible
    chrome_windows = [w for w in gw.getWindowsWithTitle('Chrome') if w.visible]

    for win in chrome_windows:
        try:
            app = Application().connect(handle=win._hWnd)
            app_window = app.window(handle=win._hWnd)
            app_window.minimize()
        except Exception as e:
            print(f"Не вдалося згорнути: {e}")


def convert_time(sentence):
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
    except:
        print('An error occured')


def set_timer(amount):
    time.sleep(amount)
    print("⏰ Час вийшов!")

    # Звук (тільки для Windows)
    try:
        winsound.Beep(1000,1000)
        #speak('Beep!!, Beep!!, Timer is out STAND UP!')
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/Beep!!, Beep!!, Timer is out STAND UP!.mp3"))  # частота 1000Гц, тривалість 1 сек
    except:
        print("🔔 Дзвінок!")


async def handle_weather(command):

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


def set_alarm(target_time: datetime.time):
    while True:
        now = datetime.datetime.now().time()
        if now.hour == target_time.hour and now.minute == target_time.minute:
            #speak('ALARM, ALARM, the clock is out. You must to go to do something')
            playsound.playsound(resource_path("'ALARM, ALARM, the clock is out. You must to go to do something'"))
            break  # інакше буде нескінченний спам
        time.sleep(1)  # затримка, щоб не навантажувати процесор


def set_alarm_clock(command):
    match = re.search(r'\b(?:[0-1]?\d|2[0-3]):(?:[0-5]\d)\b', command)
    if not match:
        print('Invalid input')
        return

    time_str = match.group()  # наприклад, "11:45"
    hour, minute = map(int, time_str.split(':'))
    alarm_time = datetime.time(hour, minute)

    speak(f'The alarm clock is set to {hour}:{minute:02d}')

    try:
        threading.Thread(target=set_alarm, args=(alarm_time,), daemon=True).start()
    except Exception as e:
        print(f'Error with thread: {e}')

                    
def gen_image(command):
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

def open_film(command):
    from parse_films import search_and_open_film
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


def get_meeting_list(lang='en'):
    meetings = memory.get_meetings()
    if not meetings:
        return "You have no scheduled meetings." if lang == 'en' else "У вас немає запланованих зустрічей."
    
    lines = ["Your meetings:" if lang == 'en' else "Ваші зустрічі:"]
    for m in meetings:
        lines.append(f"- {m['date']} at {m['time']}: {m['topic']}")
    return "\n".join(lines)


def clear_meetings_command(command):
    if "clear" in command or "очисти" in command:
        memory.clear_meetings()
        return "All meetings have been cleared."
    return None



def parse_meeting(command: str):
    command = command.lower()

    # патерн: підтримка "10:00 p.m.", "10 p.m.", "tomorrow", "for ..."
    pattern = r"(add|schedule|create|запиши|додай|створи)\s+(meeting|зустріч)\s+(at|на)?\s*(\d{1,2})([:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?\s*(today|tomorrow|завтра|сьогодні)?\s*(for|щоб)?\s*(.*)"
    match = re.search(pattern, command)

    if not match:
        return None  # патерн не підійшов

    # -------- Групи --------
    # 4 — години
    # 6 — хвилини (вкладена група в 5)
    # 7 — am/pm
    # 8 — дата (today/tomorrow)
    # 10 — тема

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


def check_meetings(json_file='memory.json', minutes_before=60):
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


def reminder_loop():
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



def search_wikipedia(query):
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

def empty_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        print("Recycle Bin cleared.")
        #speak("The recycle bin has been cleared.")
        playsound.playsound(resource_path("Jarvis_voice_commands/command_responses/The recycle bin has been cleared..mp3"))
    except Exception as e:
        print(f"Failed to clear: {e}")


def get_installed_steam_games():
    steam_path = r"C:\\Program Files (x86)\\Steam\\steamapps\\common"
    if not os.path.exists(steam_path):
        return []

    games = [name for name in os.listdir(steam_path)
             if os.path.isdir(os.path.join(steam_path, name))]
    return games

def launch_game(game_name):
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

def extract_game_name(command):
    match = re.search(r"(play|грати)\s+(.*)", command)
    if match:
        return match.group(2).strip()
    return None

async def run_voice_assistant():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        threading.Thread(target=reminder_loop, daemon=True).start()
        while True:
            command = await loop.run_in_executor(executor, wait_for_command)
            if not command:
                continue
            
            while True:
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
                    #await loop.run_in_executor(executor, speak, "You're welcome! If you need anything else, just ask.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/You're welcome! If you need anything else, just ask..mp3")
                    action_performed = True

                if 'create file' in command or 'створити файл' in command:
                    await loop.run_in_executor(executor, filehandle)
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

                if any(x in command for x in ['play the music', 'музику', 'listen music', 'слухати музику', 'play the song', 'пісню','слухати', 'play a song', 'play a music', 'play some music']):                   
                    #await loop.run_in_executor(executor, speak, "Playing a random song from your playlist.")
                    await loop.run_in_executor(executor, playsound.playsound, "Jarvis_voice_commands/command_responses/Playing a random song from your playlist..mp3")
                    await loop.run_in_executor(executor, play_music)
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
                    await loop.run_in_executor(executor, convert_time, command)
                    action_performed = True

                if 'alarm clock' in command or 'set the clock' in command:
                    await loop.run_in_executor(executor,set_alarm_clock, command)
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
                        #speak("I didn't catch your name. Please try again.")
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
                    #speak("What do you want to search on Wikipedia?")
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
                        random_responses_for_questions = random.choice(standard_responses_for_questions)
                        await loop.run_in_executor(executor, speak, random_responses_for_questions)
                        await loop.run_in_executor(executor, consultation, command)
                    else:
                        await loop.run_in_executor(executor, consultation, command)


if __name__ == "__main__":
    asyncio.run(run_voice_assistant())
