import yt_dlp
import subprocess
import os
import re
from datetime import datetime

def download_and_resize(url, resolution, video_bitrate, audio_bitrate, thread, fps=None):
    output_folder = "mp4"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if fps == "Please select frame rate (default)":
        fps = None
    
    file_name = os.path.join(output_folder, "downloaded_video.mp4")
    
    # ✅ Use yt-dlp to fetch video title
    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Fetch metadata only
        'force_filename': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Fetch video metadata
        video_title = info.get('title', 'output_video')  # Set file name from video title
        video_title = sanitize_filename(video_title)  # Sanitize file name

    # ✅ Set output file name to match the original title
    output_filename = os.path.join(output_folder, f"{video_title}.mp4")
    
    try:
        start_now = datetime.now()
        print("📥 Downloading video...")
        print(f"Start time: {start_now.strftime('%H:%M:%S')}")
        thread.yt_dlp_process = subprocess.Popen(
            ["yt-dlp", url, 
             "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",  # ✅ Force MP4 download
             "--merge-output-format", "mp4",  # ✅ Merge files into MP4
             "-o", file_name]
        )

        thread.yt_dlp_process.wait()  # Wait for download to complete

        if not thread._is_running:
            thread.yt_dlp_process.terminate()
            print("❌ Download canceled!")
            return

        # Check if the file was downloaded successfully
        if not os.path.exists(file_name):
            print(f"❌ File {file_name} not found. Download failed!")
            return

        print("🎥 Converting file with FFmpeg...")

        ffmpeg_command = [
            "ffmpeg", "-y", "-i", file_name,
            "-vf", f"scale=-1:{resolution[:-1]}",
            "-b:v", video_bitrate, "-maxrate", video_bitrate, "-bufsize", "60M",
            "-b:a", audio_bitrate, "-c:a", "aac", "-ar", "48000",
            "-c:v", "libx264", "-preset", "medium", "-r", fps if fps else "25",
            output_filename
        ]

        thread.process = subprocess.Popen(ffmpeg_command)
        
        thread.process.wait()  # Wait for FFmpeg to complete

        if not thread._is_running:
            thread.process.terminate()
            print("❌ Conversion canceled!")
            return
            
        stop_end = datetime.now()
        start_end = stop_end - start_now 
        
        print(f"End time: {stop_end.strftime('%H:%M:%S')}")
        print(f"Duration: {start_end}")
        print(f"✅ MP4 conversion successful! File saved as {output_filename}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            print("🗑️ Temporary file deleted")

def sanitize_filename(filename):
    """Remove or replace invalid characters in file name"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_mp3(url, audio_bitrate, thread):
    output_folder = "mp3"
    file_name = "downloaded_audio.m4a"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # ✅ Use yt-dlp to fetch video title
    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Fetch metadata only
        'force_filename': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # Fetch video metadata
        video_title = info.get('title', 'output_audio')  # Set file name from video title
        video_title = sanitize_filename(video_title)  # Sanitize file name

    # ✅ Set output file name to match the original title
    output_filename = os.path.join(output_folder, f"{video_title}.mp3")

    try:
        start_now = datetime.now()
        print(f"📥 Downloading MP3 with bitrate {audio_bitrate} kbps...")
        print(f"Start time: {start_now.strftime('%H:%M:%S')}")
        # 1️⃣ Download audio file with yt-dlp (without MP3 conversion)
        thread.yt_dlp_process = subprocess.Popen(
            ["yt-dlp", url, "-f", "bestaudio", "-o", file_name],
        )

        thread.yt_dlp_process.wait()  # Wait for download to complete

        # 2️⃣ Convert to MP3 using FFmpeg
        thread.process = subprocess.Popen(
            ["ffmpeg", "-y", "-i", file_name,
             "-b:a", audio_bitrate,  # 🔹 Set bitrate
             "-ar", "48000",  # 🔹 Sample rate
             "-ac", "2",  # 🔹 Stereo
             output_filename]
        )

        thread.process.wait()  # Wait for FFmpeg to complete

        if not thread._is_running:
            thread.yt_dlp_process.terminate()
            print("❌ MP3 download canceled!")
            return
        
        stop_end = datetime.now()
        start_end = stop_end - start_now 
        
        print(f"End time: {stop_end.strftime('%H:%M:%S')}")
        print(f"Duration: {start_end}")
        print(f"✅ MP3 download successful! File saved in folder {output_folder}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            print("🗑️ Temporary file deleted")