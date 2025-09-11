import os
import subprocess
from datetime import datetime
import win32com.client

from .config import THUMBNAILS_DIR

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

def find_first_video_in_directory(directory):
    """
    Пошук першого відеофайлу в директорії.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                return os.path.join(root, file)
    return None

def extract_keyframe(video_path, thumbnail_path):
    """
    Генерація ключового кадру з відео.
    """
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "select='gt(scene,0.3)',scale=320:-1",
        "-frames:v", "1",
        "-q:v", "5",
        thumbnail_path
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error for {video_path}: {e.stderr.decode('utf-8')}")

def extract_thumbnail_with_pywin32(video_path, thumbnail_path):
    """
    Спроба витягнути мініатюру за допомогою pywin32.
    """
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.Namespace(os.path.dirname(video_path))
        file = folder.ParseName(os.path.basename(video_path))
        thumbnail = file.ExtendedProperty("System.Thumbnail.Static")

        if thumbnail:
            with open(thumbnail_path, "wb") as f:
                f.write(thumbnail)
            return True
        else:
            print("No embedded thumbnail found in metadata.")
            return False
    except Exception as e:
        print(f"Error extracting thumbnail with pywin32: {e}")
        return False

def get_or_create_thumbnail(video_path):
    """
    Отримання або створення мініатюри для відео.
    """
    video_path = '\\\\?\\' + os.path.abspath(video_path)  # Підтримка довгих шляхів у Windows
    if os.path.isdir(video_path):
        folder_name = os.path.basename(video_path.rstrip('/\\'))
        video_path = find_first_video_in_directory(video_path)
        if not video_path:
            print(f"No video files found in directory: {video_path}")
            return None
        thumbnail_name = folder_name
    else:
        file_name = os.path.basename(video_path)
        thumbnail_name = os.path.splitext(file_name)[0]

    if not os.path.exists(THUMBNAILS_DIR):
        os.makedirs(THUMBNAILS_DIR)
    
    thumbnail_path = os.path.join(THUMBNAILS_DIR, f"{thumbnail_name}.jpg")

    # Перевірка існування та актуальності мініатюри
    if os.path.exists(thumbnail_path):
        video_mtime = os.path.getmtime(video_path)
        thumbnail_mtime = os.path.getmtime(thumbnail_path)
        if thumbnail_mtime > video_mtime:
            return thumbnail_path

    # Спроба витягнути мініатюру за допомогою pywin32
    if extract_thumbnail_with_pywin32(video_path, thumbnail_path):
        return thumbnail_path

    # Генерація ключового кадру
    extract_keyframe(video_path, thumbnail_path)
    return thumbnail_path
