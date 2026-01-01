# 🧠JarvisV2

Its a updated version of AI assistant JARVIS from iron man movies.
You can find previous version here.
💻[GitHub Repository](https://github.com/yourname/wordery)



## 🧱Tools
1. Speech-to-Text
  - Vosk Speech-to-Text (Model - vosk-model-small-en-us-0.15)
  - ~~Speech recognition (Python library)~~(currently not used)
2. Text-to-Speech
  - EllevenLabsAPI
  - Edge_tts
  - ~~pyttsx3(Python library)~~ (currently not used)
3. Weather
  - OpenWeatherMapsAPI
4. Brain
  - Gemini 2.0 API
5. News
  - NewsAPI
6. Camera and Screen vision
  - OpenCV


## ⚙️New Features
1. Added keyboard interrupt 'q' to quit
2. Added a bunch of new commands
  - 'recent news' - tells you all the recent news
  - 'exchange rate' - tells the dollar exchange rate
  - 'take a screenshot' - takes a screenshot and saves to folder
  - 'play the X' - plays wenewer music you say
  - 'create travel plan (location, duration, style)' - creates travel plan for u and saves in pdf file
  - 'route to X' - shows the route to any city from where you are now
  - 'roll up' - rolls up all the windows in google
  - And much more
3. Updated Memory for assistant now he can remember your name and meetings and he will remind about your meetings.
4. Background functions. Now when Jarvis launched even in waiting for wake work state. Examples:
  - Telling when your nopepad fully charged and you can unplug the charger and when your notepad has X% (You can change it) Jarvis tells you to plug your device
  - Timer. When you say set the timer to X time. After this time Jarvis will tell you that timer is out.
  - Alarm clock. Same like timer but with time when to alarm your.

## 🛠How to launch
Open any code editor create a folder paste this commands in terminal
Now there are 2 versions
- Jarvis_vosk - stable
- Jarvis_V2 - some functions may not work but works in multi-threading and async.
```bash
git clone https://github.com/Orestver/JarvisV2
pip install -r requirements.txt
py Jarvis_vosk.py

or
```bash
git clone https://github.com/Orestver/JarvisV2
pip install -r requirements.txt
py Jarvis_V2.py

Hope that was interesting for you :D.
