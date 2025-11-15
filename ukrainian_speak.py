
from gtts import gTTS
from playsound import playsound
import os

def speak(txt, lang='uk'):
    tts = gTTS(text=txt, lang=lang)
    tts.save("output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")
