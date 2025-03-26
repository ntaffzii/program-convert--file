# Program Convert File (MP3 & MP4)

## **Installing yt-dlp and FFmpeg**

To use this program, you need to install **yt-dlp** and **FFmpeg** first. Follow these steps:

### 1. **Install yt-dlp**
- Open your working environment.
- Run the following command:
  ```bash
  pip install yt-dlp
  ```

If it’s already installed but not working, run this command to upgrade:

  ```bash
  pip install --upgrade yt-dlp
  ```
### 2. **Install FFmpeg:**

 - FFmpeg is a program used for converting video and audio files.
 - Go to the FFmpeg Download website and select your operating system.
 - For Windows:
    - Click on Windows builds from gyan.dev.
    - Download the .zip file and extract it.
    - You will get a bin/ folder that contains the ffmpeg.exe file.

### 3. **Set up PATH for FFmpeg:**

 - Copy the path of the bin/ folder (e.g., C:\ffmpeg\bin).
 - Press Win + R, type sysdm.cpl, and press Enter.
 - Go to the Advanced tab and click on Environment Variables.
 - In the System variables section, select Path and click on Edit.
 - Click New and paste the copied path (e.g., C:\ffmpeg\bin).
 - Click OK and restart your computer once.

### 4. **Test the FFmpeg installation:**

 - Open cmd or PowerShell and type:
   ```bash
    ffmpeg -version
    ```

If the version of FFmpeg appears, the installation was successful.
If you see "command not found," please check your PATH settings again.
