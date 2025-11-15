import pytube
import os
def download_video(video_url):
    try:
        os.makedirs('videos', exist_ok=True)
        yt = pytube.YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download('videos', filename_prefix='downloaded_')
        print(f"Downloaded: {yt.title}")

    except Exception as e:
        print(f'Error downloading video {e}')

download_video('https://www.youtube.com/watch?v=0MhVkKHYUAY')