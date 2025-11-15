import pyttsx3
import os, winreg, subprocess
import re
def create_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    return engine

def speak(text):  # <-- обов'язково передаємо екземпляр UI
    engine = create_tts_engine()
    engine.say(text)
    engine.runAndWait()
  
import os
import winreg

def find_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        return steam_path
    except Exception as e:
        print("❌ Не вдалося знайти Steam через реєстр:", e)
        return None
    
def get_all_steam_libraries():
    try:
        steam_path = find_steam_path()
        if not steam_path:
            return []

        library_vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(library_vdf_path):
            print("❌ Не знайдено файл libraryfolders.vdf.")
            return []

        with open(library_vdf_path, encoding="utf-8") as f:
            content = f.read()

        # Знаходимо всі рядки типу: "path"    "D:\\SteamLibrary"
        paths = re.findall(r'"path"\s+"([^"]+)"', content)
        # Додаємо steamapps у кінець
        steamapps_paths = [os.path.join(path, "steamapps") for path in paths]

        return steamapps_paths
    except Exception as e:
        print("❌ Помилка при зчитуванні Steam бібліотек:", e)
        return []

def get_installed_steam_games():
    libraries = get_all_steam_libraries()
    all_games = []

    for lib in libraries:
        common_path = os.path.join(lib, "common")
        if not os.path.exists(common_path):
            continue

        games = [name for name in os.listdir(common_path)
                 if os.path.isdir(os.path.join(common_path, name))]
        all_games.extend(games)

    print(f"✅ Знайдено {len(all_games)} встановлених ігор:")
    print("🎮 " + ", ".join(all_games))
    return all_games




def find_executable_in_game_folder(game_path, game_name):
    # Пробуємо знайти .exe, що містить назву гри
    for root, dirs, files in os.walk(game_path):
        for file in files:
            if file.lower().endswith(".exe") and game_name.lower() in file.lower():
                return os.path.join(root, file)
    return None



def get_launchable_steam_games():
    libraries = get_all_steam_libraries()
    launchable_games = {}

    for lib in libraries:
        common_path = os.path.join(lib, "common")
        if not os.path.exists(common_path):
            continue

        for game_folder in os.listdir(common_path):
            game_path = os.path.join(common_path, game_folder)
            if not os.path.isdir(game_path):
                continue

            exe_path = find_executable_in_game_folder(game_path, game_folder)
            if exe_path:
                launchable_games[game_folder] = exe_path

    print(f"✅ Знайдено {len(launchable_games)} ігор, які можна запустити:")
    for name, path in launchable_games.items():
        print(f"🎮 {name} → {path}")
    return launchable_games


def launch_game(game_name, games_dict):
    for name, path in games_dict.items():
        if game_name.lower() in name.lower():
            print(f"🚀 Запуск {name} → {path}")
            subprocess.Popen(path)
            return True
    print(f"❌ Не вдалося знайти гру '{game_name}' серед встановлених.")
    return False

if __name__ == "__main__":
    launchable = get_launchable_steam_games()

    command = "play terraria"
    if "play" in command:
        game_name = command.replace("play", "").strip()
        launch_game(game_name, launchable)