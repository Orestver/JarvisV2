from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import os, playsound

load_dotenv()
elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)
def speak(txt,filename):
    audio_stream = elevenlabs.text_to_speech.convert(
        text=txt,
        voice_id="U4IxWQ3B5B0suleGgLcn", #U4IxWQ3B5B0suleGgLcn - для віри
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    audio_bytes = b"".join(audio_stream)
    with open(filename, "wb") as f:
        f.write(audio_bytes)
        
os.makedirs("Vira_voice_commands/command_responses", exist_ok=True)

standart_responses = [
   "Що вихочете знайти на вікіпедії."

]

for i, phrase in enumerate(standart_responses):
    filename = f"Vira_voice_commands/command_responses/{phrase}.mp3"
    speak(phrase, filename)
import os


