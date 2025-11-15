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
from weather_forecast import WeatherForecast
import playsound
from datetime import timedelta
from dotenv import load_dotenv
import json
from memory_manager import AssistantMemory
import ctypes
import wikipedia
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
memory = AssistantMemory()
#change if plan is over
#from speak import speak
#from elevenlabsspeach import speak
#from main import speak
from ukrainian_speak import speak

standard_responses_for_questions = [
    "Секундочку",
    "Хвилиночку, Сер",
    "Займаюсь цим, Сер",
    "Зараз, Сер"
]


standart_responses = [
    "Звісно Сер",
    "Хвилиночку, Сер",
    "Секундочку",
]

def extract_voice_command(folder_path="Vira_voice_commands/standart_responses"):
# Отримаємо список всіх mp3-файлів у папці
    audio_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith(".mp3")
    ]
    return audio_files

def save_to_pdf(text):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"travel_plan_{now}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
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
        print(f"Ваш план успішно створений у {filename}")
        return filename

def save_musics_json():
    import json
    with open('musics.json', 'w') as file:
        json.dump(musics, file, indent=4)
    print("Музику додано у musics.json.")


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
        print("Слухаю...")
        audio = recognizer.listen(source)
    try:
        command_text = recognizer.recognize_google(audio, language='uk-UA')# ukrainian - uk-UA english - en-US
        print(f"Розпізнана команда: {command_text}")
        return command_text.lower()
    except sr.UnknownValueError:
        print("НЕ зрозуміла.")
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
        print("🎧 Чекаю на слово...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command_text = recognizer.recognize_google(audio, language='uk-UA') # ukrainian - uk-UA english - en-US
        print(f"🔊 Почула: {command_text}")

        if 'jarvis' in command_text.lower(): #джарвіс
            speak("Yes Sir")
            wishMe()  # ← Додаємо вітання тут
            return "smth"  # повертаємо пусто, щоб перейти у while-loop
        if 'віра' in command_text.lower():
            #speak("Так рада знову вас чути Сер")
            playsound.playsound("Vira_voice_commands/command_responses/Glad to see you.mp3")
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
        f"You're Vira, an AI voice assistant female, speaking to the user in a natural, friendly tone. "
        'You are very good girl, you are very helpful and you always try to help the user. '
        f"Speak like you speak with human and i tell you: '{command}'. "
        "Dont use unicode characters, just use normal letters. "
        "Speak casually and clearly, like you're explaining something out loud to a person. "
        "Use contractions and natural language, as if you're talking in a normal conversation. "
        "Don't use greetings or closings, just start answering right away, and also dont give such a long answer, "
        "Avoid technical jargon unless necessary. Keep it short and helpful."
        "Dont give so long answers hust a few sentenses"
        "Give responses in ukrainian language"
    )
    
    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
    response_text = response.text.strip()
    if response_text:
        speak(response_text)
        print(f"Віра: {response_text}")
        print("Відповідь отримано успішно .")
    else:
        speak("Вибачте, я не знайшла відповіді на ваше питання. Будь ласка, спробуйте ще раз пізніше або запитайте щось інше.")
        print("⚠️ No response from AI. Please try again later or ask something else.")


def generate_prompt(command):
    #speak("Генерую промт для планування подорожі...")
    playsound.playsound("Vira_voice_commands/command_responses/Creating prompt.mp3")
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
            "give response in ukrainian language")
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    prompt_text = response.text.strip()
    if prompt_text:
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
    playsound.playsound("Vira_voice_commands/command_responses/Plan is ready.mp3")
    #speak("Ваш план подорожі складений успішно.")
    return plan_text
    

def check_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    weekday_index = now.weekday()  # 0–6
    days = {
        0: "Понеділок", 
        1: "Вівторок", 
        2: "Середа", 
        3: "Четвер", 
        4: "П'ятниця", 
        5: "Субота", 
        6: "Неділя"
    }

    current_day = days[weekday_index]
    print(f"Зараз: {current_time}, і сьогодні: {current_day}")
    speak(f"Зараз: {current_time}, і сьогодні: {current_day}")


def wishMe():
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour < 12:
        playsound.playsound("Vira_voice_commands/greetings/Good morning.mp3")
        #speak("Доброго ранку Сер!")
    elif hour >= 12 and hour < 18:
        playsound.playsound("Vira_voice_commands/greetings/Good afternoon.mp3")
        #speak("Добрийдень Сер!")
    else:
        playsound.playsound("Vira_voice_commands/greetings/Good evening.mp3")


def volume_control(command):
    match = re.search(r'\d+', command)
    if not match:
        return
    try:
        volume = int(match.group())
        if 0 <= volume <= 100:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(
                        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                    volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)
                    speak(f"Гучність встановлено на {volume} відсотків.")
        else:
                    speak("Встановіть нормальний рівень гучності від 0 до 100.")
    except ValueError:
            speak("Невірний рівень гучності. Будь ласка, введіть число від 0 до 100.")


def mute_control(command):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
    if 'mute' in command:
        speak("Мучу систему.")
        print("Мучу систему.")
    elif 'unmute' in command:
        speak("Розмучую систему.")
        print("Розмучую систему.")
    if volume_control.GetMute():
        volume_control.SetMute(0, None)
        speak("Unmuted.")
    else:
        volume_control.SetMute(1, None)
        speak("Muted.")


def opener(command):
    if 'youtube' in command or 'ютуб' in command:
        #speak("Відкриваю Ютуб.")
        #speak("Що ви хочете знайти на Ютубі?")
        playsound.playsound("Vira_voice_commands/command_responses/Open Youtube.mp3")
        playsound.playsound("Vira_voice_commands/command_responses/What to search in youtube.mp3")
        query = command_req()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        speak(f"Шукаю {query} на Ютубі.")
        webbrowser.open(url)

    elif 'google' in command or 'гугл' in command:
        #speak("Відкриваю Гугл.")
        #speak("What do you want to search.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening Google.mp3")
        playsound.playsound("Vira_voice_commands/command_responses/What to search in Google.mp3")
        query = command_req()
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        speak(f"Searching for {query} on Google.")
        webbrowser.open(url)

    elif 'telegram' in command or 'телеграм' in command:
        #speak("Відкриваю телеграм.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening telegram.mp3")
        os.system("start https://web.telegram.org")

    elif 'github' in command or 'гітхаб' in command:
        playsound.playsound("Vira_voice_commands/command_responses/Opening GitHub.mp3")
        #speak("Відкриваю Гітхаб.")
        os.system("start https://github.com")
    elif 'instagram' in command or 'інстаграм' in command:
        playsound.playsound("Vira_voice_commands/command_responses/Opening instagram.mp3")
        #speak("Відкриваю інстаграм.")
        os.system("start https://www.instagram.com")
    
    else:
        playsound.playsound("Vira_voice_commands/command_responses/Mb idk this program.mp3")
        #speak("Можливо я не знаю цю програму або сайт. Будь ласка спробуйте щераз.")


def filehandle():

    #speak("Який файл ви хочете створити? PDF, TXT, або DOCX?")
    playsound.playsound("Vira_voice_commands/command_responses/What file type.mp3")
    type = input("Enter file type (pdf/docx/txt): ").strip().lower()
    #speak("Будь ласка введіть ім'я файлу.")
    playsound.playsound("Vira_voice_commands/command_responses/please enter the title.mp3")
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
        #speak("Невірний формат файлу. Будь ласка, спробуйте ще раз.")
        playsound.playsound("Vira_voice_commands/command_responses/Invalid file format please try again.mp3")
        print("⚠️ Invalid file type. Please try again.")
        return
    try:
        with open(filename, 'w') as file:
            speak(f"File {filename} created successfully.")
            print(f"File {filename} created successfully.")
            #speak("Хочете додати вміст до файлу? (так/ні)")
            playsound.playsound("Vira_voice_commands/command_responses/Do you want to add smth in file.mp3")
            command = command_req().strip().lower()
            if 'yes' in command or 'так' in command:
                os.system(f"start {filename}")
                #speak("Ви можете додати вміст до файлу")
                playsound.playsound("Vira_voice_commands/command_responses/You can add.mp3")
            else:
                #speak("Створено пустий файл.")
                playsound.playsound("Vira_voice_commands/command_responses/Empty file created .mp3")
                print("File created without any content.")

    except Exception as e:
        speak(f"An error occurred while creating the file: {e}")
        print(f"⚠️ Error: {e}")


def aps(command):

    if 'calculator' in command or 'калькулятор' in command:
        #speak("Відкриваю калькулятор.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening calculator.mp3")
        os.system("start calc")
    elif 'notepad' in command or 'блокнот' in command:
        #speak("Відкриваю блокнот")
        playsound.playsound("Vira_voice_commands/command_responses/Opening notepad.mp3")
        os.system("start notepad")
    elif 'docs' in command or 'документи' in command:
        #speak("Відкриваю документи")
        playsound.playsound("Vira_voice_commands/command_responses/Opening Docs.mp3")
        webbrowser.open("https://docs.google.com/document/u/0/")
    else:
        playsound.playsound("Vira_voice_commands/command_responses/Now i idk this app.mp3")
        #speak("Наразі я не знаю цю програму. Будь ласка, спробуйте якусь іншу програму.")


def runner(command):
    #speak("Please specify the application you want to run.")
    playsound.playsound("Vira_voice_commands/command_responses/Enter the game .mp3")
    app_name = command_req().strip().lower()
    if 'gothic' in app_name or 'gothic 3' in app_name or 'gothic' in command or 'gothic 3' in command:
        #speak("Opening Gothic 3.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening Gothic 3.mp3")
        exe_path = r"D:/Gothic 3/Gothic3.exe"
        working_dir = r"D:/Gothic 3"
        subprocess.Popen(exe_path, cwd=working_dir)
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound("Vira_voice_commands/command_responses/Do you want to change the volume to 20%.mp3")
    
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound("Vira_voice_commands/command_responses/Volume set to 20%.mp3")
            playsound.playsound("Vira_voice_commands/command_responses/Enjoy your game.mp3")

    elif 'cs2' in app_name or 'counter strike 2' in app_name or 'cs2' in command or 'counter strike 2' in command:
        #speak("Opening Counter-Strike 2.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening cs2.mp3")
        subprocess.Popen(r'start steam://run/730', shell=True)
        #speak("Do you want to lower the volume to 70%?")
        playsound.playsound("Vira_voice_commands/command_responses/Do you want to change the volume to 70%.mp3")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.7, None)
            #speak("Volume set to 70%.")
            #speak("Enjoy your game!")
            playsound.playsound("Vira_voice_commands/command_responses/Volume set to 70%.mp3")
            playsound.playsound("Vira_voice_commands/command_responses/Enjoy your game.mp3")

    elif 'titan' in app_name or 'titan' in command or 'quest' in app_name or 'quest' in command:
        #speak("Opening Titan Quest.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening Titan Quest..mp3")
        subprocess.Popen(r'start steam://run/475150', shell=True)
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound("Vira_voice_commands/command_responses/Do you want to change the volume to 20%.mp3")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound("Vira_voice_commands/command_responses/Do you want to change the volume to 20%.mp3")
            playsound.playsound("Vira_voice_commands/command_responses/Enjoy your game.mp3")
    elif 'terraria' in app_name or 'terraria' in command:
        #speak("Opening Terraria.")
        playsound.playsound("Vira_voice_commands/command_responses/Opening Terraria.mp3")
        subprocess.Popen(r'start steam://run/105600', shell=True)
        #speak("Do you want to lower the volume to 20%?")
        playsound.playsound("Vira_voice_commands/command_responses/Do you want to change the volume to 20%.mp3")
        response = command_req().strip().lower()
        if 'yes' in response or 'так' in response:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            volume_control.SetMasterVolumeLevelScalar(0.2, None)
            #speak("Volume set to 20%.")
            #speak("Enjoy your game!")
            playsound.playsound("Vira_voice_commands/command_responses/Volume set to 20%.mp3")
            playsound.playsound("Vira_voice_commands/command_responses/Enjoy your game.mp3")
    else:
        #speak("I don't know this application. Please try again.")
        playsound.playsound("Vira_voice_commands/command_responses/Now idk this app.mp3")
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
    speak(f"Заряд батареї: {charge}%")
    speak(f"Використання процесора: {cpu_usage}%")
    speak(f"Пам'ять: {total_memory:.2f} GB")
    speak(f"Використана пам'ять: {used_memory:.2f} GB")
    speak(f"Вільна пам'ять: {free_memory:.2f} GB")

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
    #speak("Please enter the name of the song you want to add.")
    playsound.playsound("Vira_voice_commands/command_responses/Enter the song name.mp3")
    song_name = input("Enter song name: ").strip().lower() 
    #speak("Please enter the YouTube link for the song.")
    playsound.playsound("Vira_voice_commands/command_responses/Paste the link to song.mp3")
    song_link = input("Enter YouTube link: ").strip()
    
    if song_name and song_link:
        musics[song_name] = song_link
        save_musics_json()
        speak(f"Song '{song_name}' added successfully.")
        print(f"Song '{song_name}' added successfully.")
    else:
        speak("Invalid input. Please try again.")
        playsound.playsound("Vira_voice_commands/command_responses/Invalid input try again.mp3")
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
    if 'години'in sentence or 'годин' in sentence or 'годину' in sentence:
        seconds = time*3600
        speak(f'Таймер встановлено на  {time} годин')
    elif 'хвилини'in sentence or 'хвилину' in sentence or 'хвилин' in sentence:
        seconds = time*60
        speak(f'Таймер встановлено на {time} хвилин')

    elif 'секунди'in sentence or 'секунд' in sentence or 'секунду' in sentence:
        seconds = time
        speak(f'Таймер встановлено на {seconds} Секунд')
    else:
        print('Неправильний формат вводу спробуйте години хвилини або секунди')
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
        #speak('Beep!!, Beep!!, it seems like timer is out')
        playsound.playsound("Vira_voice_commands/command_responses/Timer out.mp3")  # частота 1000Гц, тривалість 1 сек
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
    playsound.playsound("Vira_voice_commands/command_responses/Can i get a location.mp3")
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
        playsound.playsound("Vira_voice_commands/command_responses/Ok than enter city.mp3")


def set_alarm(target_time: datetime.time):
    while True:
        now = datetime.datetime.now().time()
        if now.hour == target_time.hour and now.minute == target_time.minute:
            #speak('ALARM, ALARM, the clock is out. You must to go to do something')
            playsound.playsound("Vira_voice_commands/command_responses/The time is out.mp3")
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

    speak(f'Будильник встановлено на  {hour}:{minute:02d}')

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
        playsound.playsound("Vira_voice_commands/command_responses/Enjoy watching.mp3")
    else:
        #speak('Something went wrong try again')
        playsound.playsound("Vira_voice_commands/command_responses/Smth went wrong try again.mp3")


def get_meeting_list(lang='en'):
    meetings = memory.get_meetings()
    if not meetings:
        return "You have no scheduled meetings." if lang == 'en' else "У вас немає запланованих зустрічей."
    
    lines = ["Your meetings:" if lang == 'en' else "Ваші зустрічі:"]
    for m in meetings:
        lines.append(f"- {m['date']} at {m['time']}: {m['topic']}")
    return "\n".join(lines)


def clear_meetings_command(command):
    if "clear" in command or "очисти" in command or 'видали зустрічі' in command:
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

def search_wikipedia(query):

    try:
        wikipedia.set_lang("ua")  # або "en" для англійської
        summary = wikipedia.summary(query, sentences=2)  # 2 речення
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Занадто багато значень: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Сторінку не знайдено."
    except Exception as e:
        return f"Сталася помилка: {e}"
    
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
                speak(f"Нагадую про зустріч о {reminder['time_str']}: {reminder['topic']}")
                already_reminded[meeting_id] = now

        time.sleep(CHECK_INTERVAL)


def empty_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        print("Recycle Bin cleared.")
        #speak("The recycle bin has been cleared.")
        playsound.playsound("Jarvis_voice_commands/command_responses/The recycle bin has been cleared..mp3")
    except Exception as e:
        print(f"Failed to clear: {e}")

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
                if any(x in command for x in ['який день', 'час', 'година', 'дата']):
                    await loop.run_in_executor(executor, check_time)
                    action_performed = True

                if 'звук' in command or 'гучність' in command:
                    await loop.run_in_executor(executor, volume_control, command)
                    action_performed = True

                if any(x in command for x in ['замуть', 'розмуть', 'вимкнути', 'увімкнути']):
                    
                    await loop.run_in_executor(executor, mute_control, command)
                    action_performed = True

                if any(x in command for x in ['youtube', 'ютуб', 'google', 'гугл', 'telegram', 'телеграм', 'github', 'гітхаб']):
                    await loop.run_in_executor(executor, opener, command)
                    action_performed = True

                if any(x in command for x in ['exit', 'вихід', 'turn off', 'bye','па-па','добраніч', 'надобраніч','прощавай', 'бувай']):
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Bye i will be waiting for u.mp3")
                    #await loop.run_in_executor(executor, speak, "Папа, буду чекати на вас знову, Сер")
                    action_performed = True
                    break

                if 'створи файл' in command or 'створити файл' in command:
                    await loop.run_in_executor(executor, filehandle)
                    action_performed = True

                if any(x in command for x in ['calculator', 'калькулятор', 'notepad', 'блокнот', 'docs', 'документи','documents']):
                    await loop.run_in_executor(executor, aps, command)
                    action_performed = True

                if  'очистити консоль' in command:
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Clearing the console.mp3")
                    #await loop.run_in_executor(executor, speak, "Clearing the console.")
                    os.system('cls' if os.name == 'nt' else 'clear')
                    action_performed = True

                if 'запусти' in command or 'запустити' in command:
                    await loop.run_in_executor(executor, runner, command)
                    action_performed = True

                if any(x in command for x in ['перевір стан системи', 'систему', 'система']):    
                    #await loop.run_in_executor(executor, speak, "Checking system information.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Checking sys.mp3")
                    await loop.run_in_executor(executor, sysinfo)
                    action_performed = True

                if any(x in command for x in ['включи пісню', 'включи музику', 'ввімкни музику', 'слухати музику', 'увімкни музику', 'включити пісню','слухати пісню', 'включити музику', 'play a music']):                   
                    #await loop.run_in_executor(executor, speak, "Включаю пісню для тебе.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Turning music for u.mp3")
                    await loop.run_in_executor(executor, play_music)
                    time.sleep(3)
                    await loop.run_in_executor(executor, roll_up)
                    #await loop.run_in_executor(executor, speak, "Насолоджуйтеся)))) музикою!")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Enjoy your music.mp3")
                    action_performed = True
 
                if 'додай пісню' in command or 'додати музику' in command:                   
                    await loop.run_in_executor(executor, add_music)
                    action_performed = True

                if 'shutdown' in command or 'вимкнути' in command:
                    #await loop.run_in_executor(executor, speak, "Are you sure you want to shut down the system? Say 'yes' or 'no'.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Are you sure to turn off.mp3") 
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        #await loop.run_in_executor(executor, speak, "Shutting down the system.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/turning off pc.mp3") 
                        os.system("shutdown /s /t 1")
                    else:
                        #await loop.run_in_executor(executor, speak, "Shutdown cancelled.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Turning off canceled.mp3") 
                    action_performed = True

                if 'restart' in command or 'перезавантажити' in command:
                    #await loop.run_in_executor(executor, speak, "Are you sure you want to restart the system? Say 'yes' or 'no'.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Are you sure to restart pc.mp3")
                    confirmation = await loop.run_in_executor(executor, command_req)
                    if confirmation.strip().lower() in ['yes', 'так']:
                        #await loop.run_in_executor(executor, speak, "Restarting the system.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Restarting pc.mp3")
                        os.system("shutdown /r /t 1")
                    else:
                        #await loop.run_in_executor(executor, speak, "Restart cancelled.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Restarting canceled.mp3")
                    action_performed = True

                if 'погоду' in command or 'погода' in command:
                    await handle_weather(command)
                    action_performed = True


                if 'маршрут' in command or 'маршрут' in command or 'напрямок' in command or 'дорога' in command  :
                    #await loop.run_in_executor(executor, speak, "Please enter the destination address.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Please enter the city.mp3")

                    destination = input("Введіть місто: ").strip()
                    if destination:
                        url = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(destination)}"
                        webbrowser.open(url)
                        await loop.run_in_executor(executor, speak, f"Відкриваю шлях до {destination} на Гугл картах.")
                    else:
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Invalid name. Try again.mp3")

                        #await loop.run_in_executor(executor, speak, "Invalid destination address. Please try again.")
                    action_performed = True

                if any(x in command for x in ['склади план подорожі', 'план подорожі', 'create travel plan', 'подорож', 'Journay']):
                    create_plan_prompt = await loop.run_in_executor(executor, generate_prompt, command)
                    await loop.run_in_executor(executor, create_plan, create_plan_prompt)
                    action_performed = True

                if 'згорни' in command or 'згорнути' in command:
                    await loop.run_in_executor(executor, roll_up)
                    action_performed = True

                if 'таймер' in command or 'постав таймер' in command:               
                    await loop.run_in_executor(executor, convert_time, command)
                    action_performed = True

                if 'будильник' in command or 'постав будильник' in command:
                    await loop.run_in_executor(executor,set_alarm_clock, command)
                    action_performed = True
                    #need paid status
                if 'generate image' in command or 'create image' in command:
                    await loop.run_in_executor(executor, gen_image,command)
                    action_performed = True

                if 'подивитися' in command or 'включи фільм' in command or 'ввімкни фільм' in command:
                
                    await loop.run_in_executor(executor, open_film, command)
                    action_performed = True

                if 'дякую' in command or 'вдячний' in command:
                    #await loop.run_in_executor(executor, speak, "You're welcome! If you need anything else, just ask.")
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/no problem.mp3")
                    action_performed = True

                if 'хто я' in command or 'як мене звати' in command or "яке в мене ім'я" in command:
                    name = memory.recall("name")
                    if name:
                        await loop.run_in_executor(executor, speak, f"Звісно ти {name}.")
                    else:
                        #await loop.run_in_executor(executor, speak, "I don't know your name yet. Please tell me your name first.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Idk your name yet.mp3")
                    action_performed = True
                elif 'мене звати' in command or "моє ім'я" in command or 'мене звуть' in command:
                    match = re.search(r'(мене звати|моє ім\'я|мене звуть|my name)\s+(.+)', command)
                    if match:
                        name = match.group(2)
                        memory.remember("name", name)
                        print(f"Запам'ятала: {name}")
                    else:
                        #speak("I didn't catch your name. Please try again.")
                        playsound.playsound("Vira_voice_commands/command_responses/I didnt catch your name.mp3")
                        print("Я не почула твого імені, спробуй ще раз")
                    action_performed = True

                if any(trigger in command for trigger in ["додай зустріч", "запиши зустріч", "запам'ятай зустріч", 'add meetings', 'add a meeting']):
                    meeting = parse_meeting(command)
                    if meeting:
                        memory.add_meeting(meeting["date"], meeting["time"], meeting["topic"])
                        await loop.run_in_executor(executor, speak, f"Зустріч о {meeting['time']} на  {meeting['date']} збережено: {meeting['topic']}")
                    else:
                        #await loop.run_in_executor(executor, speak, "I didn't understand the meeting time or format.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/I didnt understand the meeting time.mp3")
                    action_performed = True

                if any(trig in command for trig in ['покажи зустрічі', 'які я маю зустрічі', 'які зустрічі', 'покажи зустрічі','які в мене зустрічі','які в мене є зустрічі','покажи мої зустрічі']):
                    lang = 'en' if 'what' in command or 'show' in command else 'ua'
                    result = get_meeting_list(lang)

                    await loop.run_in_executor(executor, speak, result)
                    await loop.run_in_executor(executor, print, result)
                    action_performed = True

                if "clear meetings" in command or "очисти зустрічі" in command or 'видали всі зустрічі' in command or 'видали зустрічі' in command:
                    result = clear_meetings_command(command)
                    if result:
                        await loop.run_in_executor(executor, speak, result)
                        action_performed = True
                if 'close browser' in command or 'закрий браузер' in command or 'закрити браузер' in command or 'закрий гугл' in command:
                    #speak('Closing all browser windows.')
                    playsound.playsound("Vira_voice_commands/command_responses/Close all windows.mp3")
                    os.system('taskkill /f /im chrome.exe')  # Замість chrome.exe можна використовувати інший браузер
                    action_performed = True

                if 'очистити корзину' in command or 'очисти корзину' in command or 'очисти кошик' in command or 'очистити кошик' in command:
                    await loop.run_in_executor(executor, empty_recycle_bin)
                    await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/Bin cleared.mp3")
                    action_performed = True
                if 'вікіпелію' in command or 'вікіпедія' in command:
                    #speak("What do you want to search on Wikipedia?")
                    playsound.playsound("Vira_voice_commands/command_responses/What do you want to search in wikipedia.mp3")
                    query = await loop.run_in_executor(executor, command_req)
                    if query:
                        result = search_wikipedia(query)
                        await loop.run_in_executor(executor, speak, result)
                        await loop.run_in_executor(executor, print, result)
                        action_performed = True
                    else:
                        #await loop.run_in_executor(executor, speak, "I didn't catch your query. Please try again.")
                        await loop.run_in_executor(executor, playsound.playsound, "Vira_voice_commands/command_responses/I didnt catch your query.mp3")
                        print("Я не зрозуміла ваш запит, будь ласка спробуйте ще раз.")
                        action_performed = True
                if not action_performed:
                    
                    if any(x in command for x in ['?', 'що', 'хто', 'як', 'чому']):
                        await loop.run_in_executor(executor, consultation, command)
                    else:
                        await loop.run_in_executor(executor, consultation, command)

if __name__ == "__main__":
    asyncio.run(run_voice_assistant())
