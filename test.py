import asyncio
import concurrent.futures
import random
import pyttsx3
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
import webbrowser
import urllib.parse
import subprocess
import psutil
import pygetwindow as gw
from pywinauto.application import Application
# Імпортуємо всі необхідні функції, які не змінюються


from dotenv import load_dotenv
load_dotenv()

from weather_forecast import WeatherForecast  # Імпортуємо клас WeatherForecast з weather_forecast.py
# Load environment variables from .env file



GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
command_queue = asyncio.Queue()
current_task = None
stop_event = asyncio.Event()

standard_responses_for_questions = [
    "Loading... Sir",
    "Processing...",
    "Just a moment, Sir.",
    "Let me think about that, Boss.",
    "I'm on it, Sir.",
    "Give me a second, Boss."
]


standart_responses = [
    "Sure, Boss.",
    "Of course, Sir.",
    "Just a moment, Sir.",
    "I'm on it, Sir.",
    "Give me a second, Boss."
]

def continuous_listener(loop, command_queue):
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000  # Set energy threshold for ambient noise
    recognizer.dynamic_energy_threshold = True  # Enable dynamic energy thresholding
    recognizer.pause_threshold = 0.8  # Set pause threshold for recognizing speech
    recognizer.non_speaking_duration = 0.5  # Set non-speaking duration for recognizing speech
    recognizer.operation_timeout = 10  # Set operation timeout for speech recognition
    recognizer.phrase_threshold = 0.5  # Set phrase threshold for recognizing speech
    recognizer.recognize_timeout = 5  # Set timeout for recognizing speech
    recognizer.recognize_silence_timeout = 5  # Set timeout for silence in speech recognition
    recognizer.energy_ratio_threshold = 1.5  # Set energy ratio threshold for recognizing speech
    recognizer.dynamic_energy_adjustment_damping = 0.15  # Set damping for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_ratio = 1.5  # Set ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_threshold = 0.5  # Set threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing = 0.1  # Set smoothing for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_ratio = 0.5  # Set smoothing ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_threshold = 0.5  # Set smoothing threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_damping = 0.1  # Set damping for dynamic energy adjustment smoothing
    mic = sr.Microphone()

    while True:
        with mic as source:
            print("🎙️ Слухаю...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio, language='en-US').lower()
            print(f"🔊 Розпізнано: {command}")
            asyncio.run_coroutine_threadsafe(command_queue.put(command), loop)
        except sr.UnknownValueError:
            continue

async def run_command(loop, executor, func, *args):
    global current_task, stop_event
    stop_event.clear()

    def wrapper():
        func(*args)
        return

    current_task = loop.run_in_executor(executor, wrapper)
    await current_task

def save_to_pdf(text):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"travel_plan_{now}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
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


def create_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)           # Швидкість мовлення
    engine.setProperty('volume', 1.0)       # Гучність
    voices = engine.getProperty('voices')
    voice_index = 1
    if voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    else:
        print("⚠️ Вказано некоректний індекс голосу, використовується голос за замовчуванням.")
    
    return engine


def speak(text):
    engine = create_tts_engine()
    engine.say(text)
    engine.runAndWait()


def command_req():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000  # Set energy threshold for ambient noise
    recognizer.dynamic_energy_threshold = True  # Enable dynamic energy thresholding
    recognizer.pause_threshold = 0.8  # Set pause threshold for recognizing speech
    recognizer.non_speaking_duration = 0.5  # Set non-speaking duration for recognizing speech
    recognizer.operation_timeout = 10  # Set operation timeout for speech recognition
    recognizer.phrase_threshold = 0.5  # Set phrase threshold for recognizing speech
    recognizer.recognize_timeout = 5  # Set timeout for recognizing speech
    recognizer.recognize_silence_timeout = 5  # Set timeout for silence in speech recognition
    recognizer.energy_ratio_threshold = 1.5  # Set energy ratio threshold for recognizing speech
    recognizer.dynamic_energy_adjustment_damping = 0.15  # Set damping for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_ratio = 1.5  # Set ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_threshold = 0.5  # Set threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing = 0.1  # Set smoothing for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_ratio = 0.5  # Set smoothing ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_threshold = 0.5  # Set smoothing threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_damping = 0.1  # Set damping for dynamic energy adjustment smoothing

    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
    try:
        command_text = recognizer.recognize_google(audio, language='en-US')
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
    recognizer.energy_threshold = 4000  # Set energy threshold for ambient noise
    recognizer.dynamic_energy_threshold = True  # Enable dynamic energy thresholding
    recognizer.pause_threshold = 0.8  # Set pause threshold for recognizing speech
    recognizer.non_speaking_duration = 0.5  # Set non-speaking duration for recognizing speech
    recognizer.operation_timeout = 10  # Set operation timeout for speech recognition
    recognizer.phrase_threshold = 0.5  # Set phrase threshold for recognizing speech
    recognizer.recognize_timeout = 5  # Set timeout for recognizing speech
    recognizer.recognize_silence_timeout = 5  # Set timeout for silence in speech recognition
    recognizer.energy_ratio_threshold = 1.5  # Set energy ratio threshold for recognizing speech
    recognizer.dynamic_energy_adjustment_damping = 0.15  # Set damping for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_ratio = 1.5  # Set ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_threshold = 0.5  # Set threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing = 0.1  # Set smoothing for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_ratio = 0.5  # Set smoothing ratio for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_threshold = 0.5  # Set smoothing threshold for dynamic energy adjustment
    recognizer.dynamic_energy_adjustment_smoothing_damping = 0.1  # Set damping for dynamic energy adjustment smoothing
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command_text = recognizer.recognize_google(audio, language='en-US')
        print(f"🔊 Heard: {command_text}")

        if 'jarvis' in command_text.lower():
            speak("Yes Sir")
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
        f"Imagine you're Jarvis, an AI voice assistant, speaking to the user in a natural, friendly tone. "
        f"Dont answer speak like i speak with hume and tell you: {command}. "
        "Dont use unicode characters, just use normal letters. "
        "Speak casually and clearly, like you're explaining something out loud to a person. "
        "Use contractions and natural language, as if you're talking in a normal conversation. "
        "Don't use greetings or closings, just start answering right away, and also dont give such a long answer, "
        "Avoid technical jargon unless necessary. Keep it short and helpful."
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
    speak("Generating travel plan prompt based on your command.")
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
            "And if i dont give all data set it to default or something that you are adviced to me"
            "All the variables in the prompt must be filled")
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
    speak("Your travel plan has been created successfully.")
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
    if hour >= 0 and hour < 12:
        speak("Good morning Boss!")
    elif hour >= 12 and hour < 18:
        speak("Good afternoon Boss!")
    else:
        speak("Good evening Boss!")


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
    if stop_event.is_set():
        return
    else:
        if 'youtube' in command or 'ютуб' in command:
            speak("Opening YouTube.")
            speak("What do you want to watch on YouTube?")
            query = command_req()
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            speak(f"Searching for {query} on YouTube.")
            webbrowser.open(url)

        elif 'google' in command or 'гугл' in command:
            speak("Opening Google.")
            speak("What do you want to search.")
            query = command_req()
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            speak(f"Searching for {query} on Google.")
            webbrowser.open(url)

        elif 'telegram' in command or 'телеграм' in command:
            speak("Opening Telegram.")
            os.system("start https://web.telegram.org")

        elif 'github' in command or 'гітхаб' in command:
            speak("Opening GitHub.")
            os.system("start https://github.com")
        elif 'instagram' in command or 'інстаграм' in command:
            speak("Opening Instagram.")
            os.system("start https://www.instagram.com")
        
        else:
            speak("Maybe you want something else? Please specify.")


def filehandle():

    speak("What file do you want to create? PDF, TXT, or DOCX?")
    type = input("Enter file type (pdf/docx/txt): ").strip().lower()
    speak("Please enter the name of the file you want to create.")
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
        speak("Invalid file type. Please try again.")
        print("⚠️ Invalid file type. Please try again.")
        return
    try:
        with open(filename, 'w') as file:
            speak(f"File {filename} created successfully.")
            print(f"File {filename} created successfully.")
            speak("Do you want to write something in this file?")
            command = command_req().strip().lower()
            if 'yes' in command or 'так' in command:
                os.system(f"start {filename}")
                speak("You can write in the file now.")
            else:
                speak("File created without any content.")
                print("File created without any content.")

    except Exception as e:
        speak(f"An error occurred while creating the file: {e}")
        print(f"⚠️ Error: {e}")


def aps(command):

    if 'calculator' in command or 'калькулятор' in command:
        speak("Opening Calculator.")
        os.system("start calc")
    elif 'notepad' in command or 'блокнот' in command:
        speak("Opening Notepad.")
        os.system("start notepad")
    elif 'docs' in command or 'документи' in command:
        speak("Opening Documents.")
        webbrowser.open("https://docs.google.com/document/u/0/")
    else:
        speak("I don't know this application. Please try again.")


def runner(command):
    speak("Please specify the application you want to run.")
    app_name = command_req().strip().lower()
    if 'gothic' in app_name or 'gothic 3' in app_name or 'gothic' in command or 'gothic 3' in command:
        speak("Opening Gothic 3.")
        exe_path = r"D:/Gothic 3/Gothic3.exe"
        working_dir = r"D:/Gothic 3"
        subprocess.Popen(exe_path, cwd=working_dir)
        speak("Gothic 3 is now running.")
        speak("Do you want to lower the volume to 20%?")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            speak("Volume set to 20%.")
            speak("Enjoy your game!")

    elif 'cs2' in app_name or 'counter strike 2' in app_name or 'cs2' in command or 'counter strike 2' in command:
        speak("Opening Counter-Strike 2.")
        subprocess.Popen(r'start steam://run/730', shell=True)
        speak("Do you want to lower the volume to 70%?")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.7, None)
            speak("Volume set to 70%.")
            speak("Enjoy your game!")

    elif 'titan' in app_name or 'titan' in command or 'quest' in app_name or 'quest' in command:
        speak("Opening Titan Quest.")
        subprocess.Popen(r'start steam://run/475150', shell=True)
        speak("Do you want to lower the volume to 20%?")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            speak("Volume set to 20%.")
            speak("Enjoy your game!")
    elif 'terraria' in app_name or 'terraria' in command:
        speak("Opening Terraria.")
        subprocess.Popen(r'start steam://run/105600', shell=True)
        speak("Do you want to lower the volume to 20%?")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            speak("Volume set to 20%.")
            speak("Enjoy your game!")
    else:
        speak("I don't know this application. Please try again.")
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
    speak(f"Total Memory: {total_memory:.2f} GB")
    speak(f"Used Memory: {used_memory:.2f} GB")
    speak(f"Free Memory: {free_memory:.2f} GB")

    print(f"Battery charge: {charge}%")
    print(f"CPU Usage: {cpu_usage}%")
    print(f"Total Memory: {total_memory:.2f} GB")
    print(f"Used Memory: {used_memory:.2f} GB")
    print(f"Free Memory: {free_memory:.2f} GB")

def play_music():
    with open('musics.json', 'r') as file:
        import json
        global musics
        musics = json.load(file)
    url = random.choice(list(musics.values()))
    webbrowser.open(url)
    


def add_music():
    speak("Please enter the name of the song you want to add.")
    song_name = input("Enter song name: ").strip().lower() 
    speak("Please enter the YouTube link for the song.")
    song_link = input("Enter YouTube link: ").strip()
    
    if song_name and song_link:
        musics[song_name] = song_link
        save_musics_json()
        speak(f"Song '{song_name}' added successfully.")
        print(f"Song '{song_name}' added successfully.")
    else:
        speak("Invalid input. Please try again.")
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
        speak('Beep!!, Beep!!, it seems like timer is out')  # частота 1000Гц, тривалість 1 сек
    except:
        print("🔔 Дзвінок!")



async def run_voice_assistant():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop.run_in_executor(executor, continuous_listener, loop, command_queue)
        while True:
            command = await loop.run_in_executor(executor, wait_for_command)
            if not command:
                continue
            
            while True:
                command = await command_queue.get()
                if not command:
                    continue

                if any(x in command for x in ['whar is the time', 'час', 'date', 'дата']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, check_time)

                elif 'volume' in command or 'гучність' in command:
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, volume_control, command)

                elif any(x in command for x in ['mute', 'unmute', 'вимкнути', 'увімкнути']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, mute_control, command)

                elif any(x in command for x in ['youtube', 'ютуб', 'google', 'гугл', 'telegram', 'телеграм', 'github', 'гітхаб']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, opener, command)

                elif any(x in command for x in ['exit', 'вихід', 'turn off', 'bye']):
                    await loop.run_in_executor(executor, speak, "Goodbye! Have a great day!")
                    break

                elif 'create file' in command or 'створити файл' in command:
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, filehandle)

                elif any(x in command for x in ['calculator', 'калькулятор', 'notepad', 'блокнот', 'docs', 'документи']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, aps, command)

                elif 'help' in command or 'поміч' in command:
                    await loop.run_in_executor(executor, speak, "Here are the commands you can use: ...")

                elif 'clear' in command or 'очистити' in command:
                    await loop.run_in_executor(executor, speak, "Clearing the console.")
                    os.system('cls' if os.name == 'nt' else 'clear')

                elif 'run' in command or 'запустити' in command:
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, runner, command)

                elif any(x in command for x in ['check', 'system', 'система']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, speak, "Checking system information.")
                    await loop.run_in_executor(executor, sysinfo)

                elif any(x in command for x in ['play music', 'музика', 'listen music', 'слухати музику', 'play song', 'пісня','слухати', 'play a song', 'play a music']):
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, speak, "Playing a random song from your playlist.")
                    await loop.run_in_executor(executor, play_music)
                    await loop.run_in_executor(executor, roll_up)

                elif 'add song' in command or 'додати музику' in command:
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, add_music)

                elif 'jarvis' in command or 'джарвіс' in command:
                    await loop.run_in_executor(executor, speak, random.choice(standart_responses))
                    await loop.run_in_executor(executor, consultation, command)

                elif 'shutdown' in command or 'вимкнути' in command:
                    await loop.run_in_executor(executor, speak, "Are you sure you want to shut down the system? Say 'yes' or 'no'.")
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        await loop.run_in_executor(executor, speak, "Shutting down the system.")
                        os.system("shutdown /s /t 1")
                    else:
                        await loop.run_in_executor(executor, speak, "Shutdown cancelled.")

                elif 'restart' in command or 'перезавантажити' in command:
                    await loop.run_in_executor(executor, speak, "Are you sure you want to restart the system? Say 'yes' or 'no'.")
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        await loop.run_in_executor(executor, speak, "Restarting the system.")
                        os.system("shutdown /r /t 1")
                    else:
                        await loop.run_in_executor(executor, speak, "Restart cancelled.")

                elif 'weather' in command or 'погода' in command:
                    await loop.run_in_executor(executor, speak, "Please enter the name of the city for which you want to get the weather.")
                    df = pd.read_excel('worldcities.xlsx')  # Файл з бази SimpleMaps
                    city_list = df['city'].dropna().unique().tolist()
                    city_list_lower = [c.lower() for c in city_list]
                    city = await loop.run_in_executor(executor, command_req)
                    # Тепер перевіряємо
                    if city.lower() not in city_list_lower:
                        await loop.run_in_executor(executor, speak, "City not found in the database. Please try again.")
                        continue
                    # Знаходимо правильну назву (щоб передати в API)
                    matched_city = city_list[city_list_lower.index(city.lower())]
                    # Отримуємо погоду
                    weather = WeatherForecast()
                    await weather.get_weather(matched_city)


                elif 'route' in command or 'маршрут' in command:
                    await loop.run_in_executor(executor, speak, "Please enter the destination address.")
                    destination = input("Enter destination address: ").strip()
                    if destination:
                        url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination)}"
                        webbrowser.open(url)
                        await loop.run_in_executor(executor, speak, f"Opening route to {destination} on Google Maps.")
                    else:
                        await loop.run_in_executor(executor, speak, "Invalid destination address. Please try again.")

                        
                elif 'stop' in command or 'зупинити' in command:
                    await loop.run_in_executor(executor, speak, "Stopping the current operation.")
                    break


                elif any(x in command for x in ['travel plan', 'план подорожі', 'create travel plan', 'подорож', 'Journay']):
                    await loop.run_in_executor(executor, speak, "" + random.choice(standart_responses))
                    create_plan_prompt = await loop.run_in_executor(executor, generate_prompt, command)
                    await loop.run_in_executor(executor, create_plan, create_plan_prompt)

                elif 'roll up' in command or 'згорнути' in command:
                    await loop.run_in_executor(executor, speak, "" + random.choice(standart_responses))
                    await loop.run_in_executor(executor, roll_up)

                elif 'timer' in command or 'set the timer' in command:
                    await loop.run_in_executor(executor, speak, "" + random.choice(standart_responses))
                    await loop.run_in_executor(executor, convert_time, command)

                else:
                    if any(x in command for x in ['?', 'what', 'who', 'how', 'why']):
                        await loop.run_in_executor(executor, speak, random.choice(standard_responses_for_questions))
                        await loop.run_in_executor(executor, consultation, command)
                    else:
                        await loop.run_in_executor(executor, consultation, command)

if __name__ == "__main__":
    asyncio.run(run_voice_assistant())
