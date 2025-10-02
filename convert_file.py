import yt_dlp
import os
import re
from datetime import datetime

def download_and_resize(url, resolution, video_bitrate, audio_bitrate, thread, fps=None):
    output_folder = "mp4"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if fps == "Please select frame rate (default)":
        fps = None

    # Get video title
    ydl_opts_info = {
        'quiet': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'output_video')
        video_title = sanitize_filename(video_title)

    output_filename = os.path.join(output_folder, f"{video_title}.mp4")

    class CancelHook:
        def __init__(self, thread):
            self.thread = thread
        def hook(self, d):
            if not self.thread._is_running:
                raise yt_dlp.utils.DownloadCancelled('User cancelled download')

    try:
        start_now = datetime.now()
        print("📥 Downloading video...")
        print(f"Start time: {start_now.strftime('%H:%M:%S')}")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_filename,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'postprocessor_args': [
                '-vf', f'scale=-1:{resolution[:-1]}',
                '-b:v', video_bitrate,
                '-maxrate', video_bitrate,
                '-bufsize', '60M',
                '-b:a', audio_bitrate,
                '-c:a', 'aac',
                '-ar', '48000',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-r', fps if fps else '25',
            ],
            'progress_hooks': [CancelHook(thread).hook],
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        stop_end = datetime.now()
        start_end = stop_end - start_now

        print(f"End time: {stop_end.strftime('%H:%M:%S')}")
        print(f"Duration: {start_end}")
        print(f"✅ MP4 conversion successful! File saved as {output_filename}")

    except yt_dlp.utils.DownloadCancelled:
        print("❌ Download canceled!")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def sanitize_filename(filename):
    """Remove or replace invalid characters in file name"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_mp3(url, audio_bitrate, thread):
    output_folder = "mp3"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get video title
    ydl_opts_info = {
        'quiet': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'output_audio')
        video_title = sanitize_filename(video_title)

    output_filename = os.path.join(output_folder, f"{video_title}.mp3")

    class CancelHook:
        def __init__(self, thread):
            self.thread = thread
        def hook(self, d):
            if not self.thread._is_running:
                raise yt_dlp.utils.DownloadCancelled('User cancelled download')

    try:
        start_now = datetime.now()
        print(f"📥 Downloading MP3 with bitrate {audio_bitrate} kbps...")
        print(f"Start time: {start_now.strftime('%H:%M:%S')}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_bitrate.replace('k', ''),
            }],
            'progress_hooks': [CancelHook(thread).hook],
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        stop_end = datetime.now()
        start_end = stop_end - start_now

        print(f"End time: {stop_end.strftime('%H:%M:%S')}")
        print(f"Duration: {start_end}")
        print(f"✅ MP3 download successful! File saved in folder {output_folder}")

    except yt_dlp.utils.DownloadCancelled:
        print("❌ MP3 download canceled!")
    except Exception as e:
        print(f"❌ Error occurred: {e}")