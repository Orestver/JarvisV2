import pyttsx3
import datetime
import os, sys
import random

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import speech_recognition as sr
from google import genai
import webbrowser
import urllib.parse
import subprocess
import psutil

from dotenv import load_dotenv
load_dotenv()
# Load environment variables from .env file


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")




standard_responses_for_questions = [
    "Loading...",
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
            speak("Yes, I'm here.")
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
        f"Answer this: {command}. "
        "Dont use unicode characters, just use normal letters. "
        "Speak casually and clearly, like you're explaining something out loud to a person. "
        "Use contractions and natural language, as if you're talking in a normal conversation. "
        "Don't use greetings or closings, just start answering right away, and also dont give such a long answer, "
        "Avoid technical jargon unless necessary. Keep it short and helpful."
        "Speak like you're reading it aloud"
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


def volume_control():
    speak("Please set the volume level between 0 and 100.")
    while True:
        try:
            volume = int(command_req())
            if not volume:
                speak("No input detected. Please try again.")
                continue
            if 0 <= volume <= 100:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume_control = cast(interface, POINTER(IAudioEndpointVolume))
                volume_control.SetMasterVolumeLevelScalar(volume / 100.0, None)
                speak(f"Volume set to {volume} percent.")
                break
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



if __name__ == "__main__":
    while True:
        command = wait_for_command()
        if not command:
            pass
        else:
            while True:
                command = command_req()
                if not command:
                    continue
                else:
                    # 🔁 Повертає далі розпізнану команду
                    if ('time' in command or 'час' in command) or ('date' in command or 'дата' in command):
                        speak('' + random.choice(standart_responses))
                        check_time()
                    elif 'volume' in command or 'гучність' in command:
                        speak('' + random.choice(standart_responses))
                        volume_control()
                    elif 'mute' in command or 'unmute' in command or 'вимкнути' in command or 'увімкнути' in command:
                        speak('' + random.choice(standart_responses))
                        mute_control(command)
                    elif 'open youtube' in command or 'ютуб' in command or 'open google' in command or 'гугл' in command or 'open telegram' in command or 'телеграм' in command or 'open github' in command or 'гітхаб' in command:
                        speak('' + random.choice(standart_responses))
                        opener(command)
                    elif 'turn off' in command or 'вихід' in command or  'exit' in command or 'bye' in command:
                        speak("Goodbye! Have a great day!")
                        break
                    elif 'create file' in command or 'створити файл' in command:
                        speak('' + random.choice(standart_responses))
                        filehandle()
                    elif 'calculator' in command or 'калькулятор' in command or 'notepad' in command or 'блокнот' in command or 'docs' in command or 'документи' in command:
                        speak('' + random.choice(standart_responses))
                        aps(command)
                    elif 'help' in command or 'поміч' in command:

                        speak("Here are the commands you can use: \n"
                            "1. 'time' or 'час' - to check the current time and date.\n"
                            "2. 'volume' or 'гучність' - to adjust the system volume.\n"
                            "3. 'mute' or 'unmute' - to mute or unmute the system.\n"
                            "4. 'open youtube' or 'ютуб', 'open google' or 'гугл', 'open telegram' or 'телеграм' - to open respective websites.\n"
                            "5. 'create file' or 'створити файл' - to create a new file.\n"
                            "6. 'calculator' or 'калькулятор', 'notepad' or 'блокнот' - to open respective applications.\n"
                            "7. 'quit', 'вихід', 'exit', or 'bye' - to exit the program."
                            "8. 'clear' or 'очистити' - to clear the console."
                            "9. 'run' or 'запустити' - to run an application.\n"
                            "10. 'check system' or 'система' - to check system information.\n"
                            "11. 'play music' or 'музика', 'listen music' or 'слухати музику', 'play song' or 'пісня', 'play' or 'слухати' - to play music.\n"
                            "12. 'add song' or 'додати музику', 'song' or 'пісня' - to add a song to the music list.\n"
                            "13. 'jarvis' or 'джарвіс' - to consult with Jarvis.\n"
                            "14. Ask questions like 'what', 'who', 'how', 'why' - to get answers from Jarvis.")
                        
                    elif 'clear' in command or 'очистити' in command:
                        speak("Clearing the console.")
                        os.system('cls' if os.name == 'nt' else 'clear')
                    elif 'run' in command or 'запустити' in command:
                        speak('' + random.choice(standart_responses))
                        runner(command)
                    elif 'check' in command or 'system' in command or 'система' in command:
                        speak('' + random.choice(standart_responses))
                        speak("Checking system information.")
                        sysinfo()

                        '''
                    elif 'post' in command or 'пост' in command or 'write' in command or 'написати' in command:
                        speak("Please specify the content of the post.")
                        post_content = command_req()
                        '''

                    elif 'play music' in command or 'музика' in command or 'listen music' in command or 'слухати музику' in command or 'play song' in command or 'пісня' in command or 'play' in command or 'слухати' in command:
                        speak('' + random.choice(standart_responses))
                        play_music()

                    elif 'add song' in command or 'додати музику' in command or 'song' in command or 'пісня' in command:
                        speak('' + random.choice(standart_responses))
                        add_music()

                    elif 'jarvis' in command or 'джарвіс' in command:
                        speak('' + random.choice(standart_responses))
                        consultation(command)


                    elif 'shutdown' in command or 'вимкнути' in command or 'turn off' in command:
                        speak("Are you sure you want to shut down the system? Please confirm by saying 'yes' or 'no'.")
                        confirmation = command_req().strip().lower()
                        if 'yes' in confirmation or 'так' in confirmation:
                            speak("Shutting down the system.")
                            print("Shutting down the system.")
                            os.system("shutdown /s /t 1")
                        else:
                            speak("Shutdown cancelled.")
                            print("Shutdown cancelled.")
                            continue

                    elif 'restart' in command or 'перезавантажити' in command:
                        speak("Are you sure you want to restart the system? Please confirm by saying 'yes' or 'no'.")
                        confirmation = command_req().strip().lower()
                        if 'yes' in confirmation or 'так' in confirmation:
                            speak("Restarting the system.")
                            print("Restarting the system.")
                            os.system("shutdown /r /t 1")
                        else:
                            speak("Restart cancelled.")
                            print("Restart cancelled.")
                            continue

                    else:
                        if '?' in command or 'what' in command or 'who' in command or 'how' in command or 'why' in command:
                            speak('' + random.choice(standard_responses_for_questions))
                            consultation(command)
                        else:
                            speak('' + random.choice(standart_responses))
                            consultation(command)

