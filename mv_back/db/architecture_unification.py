import os
import shutil
from mv_back.config import *
# MOVIES_PATHS = ["D:\\KiHoXa\\Movies", "F:\\Movies"]
# SERIES_PATHS = ["E:\\Media\\Serials", "D:\\KiHoXa\\Serials", "F:\\Serials"]


def check_for_oneshot(path, type="series"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The path {path} does not exist.")
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and type == "series":
            return True
        if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mkv', '.avi')) and type == "movie":
            return True
    return False

def create_and_fill_folder(path, type="series"):
    path = r"\\?\\" + path
    mediaItems = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mkv', '.avi')):
            mediaItems.append(item_path)
    if not mediaItems:
        print(f"No files found in {path}. Skipping.")
        return
    
    if type == "series":
        season_folder = os.path.join(path, os.path.basename(path) + ' 1')
        os.makedirs(season_folder, exist_ok=True)
    for item in mediaItems:
        if type == "series":
            shutil.move(item, season_folder)
            print(f"Moved {item} to {season_folder}")
        elif type == "movie":
            movie_name = os.path.splitext(os.path.basename(item))[0]
            movie_folder = os.path.join(path, movie_name)
            os.makedirs(movie_folder, exist_ok=True)
            shutil.move(item, movie_folder)
            print(f"Moved {item} to {movie_folder}")
    return

def architecture_unification():
    for series_folder in SERIES_PATHS:
        if not os.path.exists(series_folder):
            continue
        series = os.listdir(series_folder)
        for serie in series:
            serie_path = os.path.join(series_folder, serie)
            if not check_for_oneshot(serie_path):
                create_and_fill_folder(serie_path)
    
    for movies_folder in MOVIES_PATHS:
        
        if not os.path.exists(movies_folder):
            continue
        if check_for_oneshot(movies_folder, type="movie"):
            create_and_fill_folder(movies_folder, type="movie")
    return

if __name__ == "__main__":
    architecture_unification()