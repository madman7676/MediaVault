import os
import uuid
import json
import subprocess
import win32com.client
from datetime import datetime
from config import MOVIES_PATHS, SERIES_PATHS, METADATA_FILE, BASE_URL, THUMBNAILS_DIR
from flask import Flask, request, send_file

def create_series_metadata(directory, path):
    seasons = []
    subitems = os.listdir(path)
    for subdir in subitems:
        subpath = os.path.join(path, subdir)
        if os.path.isdir(subpath):
            seasons.append({
                "title": subdir,
                "path": subpath,
                "files": [file for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
            })
    if not seasons:  # Якщо немає підпапок, створити "Season 1"
        seasons.append({
            "title": "Season 1",
            "path": path,
            "files": [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        })
    return {
        "id": str(uuid.uuid4()),
        "title": directory,
        "path": path,
        "tags": [],
        "auto_added": True,
        "last_modified": datetime.now().isoformat(),
        "type": "series",
        "seasons": seasons
    }

def create_movie_metadata(directory, path):
    parts = []
    subitems = os.listdir(path)
    for subdir in subitems:
        subpath = os.path.join(path, subdir)
        if os.path.isfile(subpath):
            parts.append({
                "title": subdir,
                "path": subpath
            })
    if not parts:  # Якщо немає файлів, пропускаємо
        return None
    return {
        "id": str(uuid.uuid4()),
        "title": directory,
        "path": path,
        "tags": [],
        "auto_added": True,
        "last_modified": datetime.now().isoformat(),
        "type": "collection",
        "parts": parts
    }

def clean_outdated_metadata(metadata):
    # Очищення серіалів
    metadata["series"] = [
        item for item in metadata["series"]
        if not item.get("auto_added", False) or os.path.exists(item["path"])
    ]
    
    # Очищення фільмів
    metadata["movies"] = [
        item for item in metadata["movies"]
        if not item.get("auto_added", False) or os.path.exists(item["path"])
    ]
    return metadata

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

def find_first_video_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                return os.path.join(root, file)
    return None

def extract_keyframe(video_path, thumbnail_path):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "select='gt(scene,0.3)',scale=320:-1",
        "-frames:v", "1",
        thumbnail_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr.decode('utf-8')}")

def get_or_create_thumbnail(video_path):
    
    if os.path.isdir(video_path):
        video_path = find_first_video_in_directory(video_path)
        if not video_path:
            print(f"No video files found in directory: {video_path}")
            return None
    
    thumbnail_path = os.path.join(THUMBNAILS_DIR, f"{os.path.basename(video_path)}.jpg")

    if os.path.exists(thumbnail_path):
        return thumbnail_path

    # Try extracting thumbnail using pywin32
    if extract_thumbnail_with_pywin32(video_path, thumbnail_path):
        return thumbnail_path
    
    extract_keyframe(video_path, thumbnail_path)
    return thumbnail_path

def extract_thumbnail_with_pywin32(video_path, thumbnail_path):
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

def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            return {"series": [], "movies": []}
    return {"series": [], "movies": []}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False, indent=4)

def auto_add_metadata(metadata, force_update=False):
    # Очищення застарілих записів
    metadata = clean_outdated_metadata(metadata)
    # Scan series
    for root_path in SERIES_PATHS:
        if os.path.exists(root_path):
            for root, dirs, files in os.walk(root_path):
                for directory in dirs:
                    path = os.path.join(root, directory)
                    existing_item = next((item for item in metadata["series"] if os.path.normpath(item["path"]) == os.path.normpath(path)), None)
                    if existing_item:
                        if force_update or existing_item["auto_added"]:
                            existing_item["last_modified"] = datetime.now().isoformat()
                            existing_item["seasons"] = []
                            subitems = os.listdir(path)
                            for subdir in subitems:
                                subpath = os.path.join(path, subdir)
                                if os.path.isdir(subpath):
                                    existing_item["seasons"].append({
                                        "title": subdir,
                                        "path": subpath,
                                        "files": [file for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
                                    })
                            if not existing_item["seasons"]:
                                existing_item["seasons"].append({
                                    "title": "Season 1",
                                    "path": path,
                                    "files": [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
                                })
                    else:
                        seasons = []
                        subitems = os.listdir(path)
                        for subdir in subitems:
                            subpath = os.path.join(path, subdir)
                            if os.path.isdir(subpath):
                                seasons.append({
                                    "title": subdir,
                                    "path": subpath,
                                    "files": [file for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
                                })
                        if not seasons:
                            seasons.append({
                                "title": "Season 1",
                                "path": path,
                                "files": [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
                            })
                        metadata["series"].append({
                            "id": str(uuid.uuid4()),
                            "title": directory,
                            "path": path,
                            "tags": [],
                            "auto_added": True,
                            "last_modified": datetime.now().isoformat(),
                            "type": "series",
                            "seasons": seasons
                        })
                break  # Only consider the top level

    # Scan movies
    for root_path in MOVIES_PATHS:
        if os.path.exists(root_path):
            for root, dirs, files in os.walk(root_path):
                for directory in dirs:
                    path = os.path.join(root, directory)
                    existing_item = next((item for item in metadata["movies"] if os.path.normpath(item["path"]) == os.path.normpath(path)), None)
                    if existing_item:
                        if force_update or existing_item["auto_added"]:
                            existing_item["last_modified"] = datetime.now().isoformat()
                            existing_item["parts"] = []
                            subitems = os.listdir(path)
                            for subdir in subitems:
                                subpath = os.path.join(path, subdir)
                                if os.path.isfile(subpath):
                                    existing_item["parts"].append({
                                        "title": subdir,
                                        "path": subpath
                                    })
                    else:
                        parts = []
                        subitems = os.listdir(path)
                        for subdir in subitems:
                            subpath = os.path.join(path, subdir)
                            if os.path.isfile(subpath):
                                parts.append({
                                    "title": subdir,
                                    "path": subpath
                                })
                        metadata["movies"].append({
                            "id": str(uuid.uuid4()),
                            "title": directory,
                            "path": path,
                            "tags": [],
                            "auto_added": True,
                            "last_modified": datetime.now().isoformat(),
                            "type": "collection",
                            "parts": parts
                        })
                for file in files:
                    path = os.path.join(root, file)
                    thumbnailUrl = f"{BASE_URL}/api/thumbnail?video_path={path}"
                    if os.path.isfile(path) and not any(os.path.normpath(item["path"]) == os.path.normpath(path) for item in metadata["movies"]):
                        metadata["movies"].append({
                            "id": str(uuid.uuid4()),
                            "title": file,
                            "path": path,
                            "tags": [],
                            "auto_added": True,
                            "last_modified": datetime.now().isoformat(),
                            "type": "collection",
                            "parts": [
                                {
                                    "title": file,
                                    "path": path,
                                    "thumbnailUrl": thumbnailUrl
                                }
                            ]
                        })
                break

    return metadata