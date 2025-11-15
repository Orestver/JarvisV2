import webbrowser
import yt_dlp
import re


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
        song_name = re.sub(r'\b(for me|please|now)\b', '', song_name).strip()
        print("Extracted song name:", song_name)
        return song_name
    return None

query = extract_song_name('could u play another love by tom odell for me please')
open_youtube_video(query)
