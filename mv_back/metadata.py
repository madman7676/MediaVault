import os
import uuid
import json
from datetime import datetime
from config import MOVIES_PATHS, SERIES_PATHS, METADATA_FILE, BASE_URL, THUMBNAILS_DIR
from flask import Flask, request, send_file

def update_paths_only(metadata, item_id):
    """
    Оновлює тільки шляхи до файлів для вказаного елемента метаданих.
    Зберігає всі інші метадані (теги, налаштування тощо).

    Parameters:
        metadata (dict): Поточні метадані
        item_id (str): ID елемента для оновлення

    Returns:
        tuple: (bool, str) - (успіх оновлення, повідомлення)
    """
    item, category = find_metadata_item(metadata, item_id=item_id)
    
    if not item or not os.path.exists(item["path"]):
        return False, "Item not found or path doesn't exist"
    try:
        if item["type"] == "series":
            print(f"Processing series: {item['title']}")
            # Отримуємо список реальних папок сезонів
            real_seasons = [d for d in os.listdir(item["path"]) 
                          if os.path.isdir(os.path.join(item["path"], d))]
            print(f"Found seasons directories: {real_seasons}")

            # --- SPECIAL CASE: Було лише один сезон, і його просто перемістили у підпапку ---
            if (
                len(item["seasons"]) == 1 and
                item["seasons"][0].get("title") == "Season 1" and
                len(real_seasons) > 0
            ):
                # Просто оновлюємо title і path першого сезону, не чіпаючи files
                item["seasons"][0]["title"] = real_seasons[0]
                item["seasons"][0]["path"] = os.path.join(item["path"], real_seasons[0])
                # Якщо з'явилися ще сезони — додаємо їх як нові
                for season_name in real_seasons[1:]:
                    season_path = os.path.join(item["path"], season_name)
                    files = [{"name": f} for f in os.listdir(season_path) if os.path.isfile(os.path.join(season_path, f))]
                    item["seasons"].append({
                        "title": season_name,
                        "path": season_path,
                        "files": files
                    })
                item["last_modified"] = datetime.now().isoformat()
                save_metadata(metadata)
                return True, "Season path updated without losing metadata"

            # Словник існуючих сезонів для збереження метаданих
            existing_seasons = {s["title"]: s for s in item["seasons"]}
            item["seasons"] = []
            
            # Для кожної реальної папки сезону
            for season_name in real_seasons:
                season_path = os.path.join(item["path"], season_name)
                # Беремо існуючий сезон або створюємо новий
                season = existing_seasons.get(season_name, {"title": season_name})
                season["path"] = season_path
                
                # Зберігаємо існуючі метадані файлів
                existing_files = {f["name"]: f for f in season.get("files", [])}
                season["files"] = []
                
                # Оновлюємо файли
                for file in os.listdir(season_path):
                    if os.path.isfile(os.path.join(season_path, file)):
                        # Зберігаємо існуючі метадані файлу або створюємо нові
                        file_data = existing_files.get(file, {})
                        file_data["name"] = file
                        season["files"].append(file_data)
                
                item["seasons"].append(season)
                print(f"Updated season {season_name} with {len(season['files'])} files")
                
        elif item["type"] == "collection":
            # Оновлюємо шляхи для фільму/колекції
            item["parts"] = [
                {
                    "title": file,
                    "path": os.path.join(item["path"], file)
                }
                for file in os.listdir(item["path"])
                if os.path.isfile(os.path.join(item["path"], file))
            ]
        
        item["last_modified"] = datetime.now().isoformat()
        save_metadata(metadata)
        return True, "Paths updated successfully"
        
    except Exception as e:
        return False, f"Error updating paths: {str(e)}"

def find_metadata_item(metadata, item_id=None, path=None):
    # Пошук запису за id або шляхом у метаданих.
    for category in ["series", "movies"]:
        for item in metadata[category]:
            if (item_id and item["id"] == item_id) or (path and os.path.normpath(item["path"]) == os.path.normpath(path)):
                return item, category
    return None, None

def create_series_metadata(directory, path):
    seasons = []
    subitems = os.listdir(path)
    for subdir in subitems:
        subpath = os.path.join(path, subdir)
        if os.path.isdir(subpath):
            seasons.append({
                "title": subdir,
                "path": subpath,
                "files": [{"name": file} for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
            })
    if not seasons:  # Якщо немає підпапок, створити "Season 1"
        seasons.append({
            "title": "Season 1",
            "path": path,
            "files": [{"name": file} for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
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
    if not os.path.isdir(path):  # Перевіряємо, чи це директорія
        return {
            "id": str(uuid.uuid4()),
            "title": os.path.basename(path),
            "path": path,
            "tags": [],
            "auto_added": True,
            "last_modified": datetime.now().isoformat(),
            "type": "collection",
            "parts": [
                {
                    "title": os.path.basename(path),
                    "path": path
                }
            ]
        }
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
    """
    Оновлює метадані для серіалів і фільмів.
    """
    metadata = clean_outdated_metadata(metadata)

    # Обробка серіалів
    metadata["series"] = process_metadata(
        SERIES_PATHS,
        metadata["series"],
        create_series_metadata,
        update_series_metadata,
        force_update
    )

    # Обробка фільмів
    metadata["movies"] = process_metadata(
        MOVIES_PATHS,
        metadata["movies"],
        create_movie_metadata,
        update_movie_metadata,
        force_update
    )

    return metadata

def update_metadata_item(existing_item, directory, path, subitem_key, subitem_creator_fn):
    """
    Оновлює запис метаданих для серіалу чи фільму.

    Parameters:
        existing_item (dict): Існуючий запис метаданих.
        directory (str): Назва директорії.
        path (str): Шлях до елемента.
        subitem_key (str): Ключ для піделементів ("seasons" чи "parts").
        subitem_creator_fn (function): Функція для створення піделементів.

    Returns:
        dict: Оновлений запис метаданих.
    """
    existing_item["last_modified"] = datetime.now().isoformat()
    existing_item[subitem_key] = []

    # Створення піделементів (сезонів або частин)
    for subdir in os.listdir(path):
        subpath = os.path.join(path, subdir)
        if subitem_creator_fn(subpath):
            existing_item[subitem_key].append({
                "title": subdir,
                "path": subpath,
                "files": [{"name": file} for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
            })

    # Додати "Season 1" або залишити порожнім, якщо немає піделементів
    if not existing_item[subitem_key] and subitem_key == "seasons":
        existing_item[subitem_key].append({
            "title": "Season 1",
            "path": path,
            "files": [{"name": file} for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        })

    return existing_item

def update_movie_metadata(existing_item, directory, path):
    existing_item["last_modified"] = datetime.now().isoformat()
    existing_item["parts"] = []

    # Додаємо частини
    for subdir in os.listdir(path):
        subpath = os.path.join(path, subdir)
        if os.path.isfile(subpath):
            existing_item["parts"].append({
                "title": subdir,
                "path": subpath
            })

    return existing_item

def update_series_metadata(existing_item, directory, path):
    existing_item["last_modified"] = datetime.now().isoformat()
    existing_item["seasons"] = []

    # Додаємо сезони
    for subdir in os.listdir(path):
        subpath = os.path.join(path, subdir)
        if os.path.isdir(subpath):
            existing_item["seasons"].append({
                "title": subdir,
                "path": subpath,
                "files": [{"name": file} for file in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, file))]
            })

    # Якщо немає сезонів, додаємо "Season 1"
    if not existing_item["seasons"]:
        existing_item["seasons"].append({
            "title": "Season 1",
            "path": path,
            "files": [{"name": file} for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        })

    return existing_item

def process_metadata(root_paths, existing_metadata, create_metadata_fn, update_metadata_fn, force_update):
    """
    Загальна функція для обробки серіалів і фільмів.

    Parameters:
        root_paths (list): Шляхи до кореневих папок.
        existing_metadata (list): Поточний список метаданих.
        create_metadata_fn (function): Функція для створення нового запису.
        update_metadata_fn (function): Функція для оновлення існуючого запису.
        force_update (bool): Прапорець для примусового оновлення метаданих.
    """
    updated_metadata = []

    for root_path in root_paths:
        if os.path.exists(root_path):
            for root, dirs, files in os.walk(root_path):
                for directory in dirs:
                    path = os.path.join(root, directory)

                    # Перевіряємо, чи запис уже існує
                    existing_item = next(
                        (item for item in existing_metadata if os.path.normpath(item["path"]) == os.path.normpath(path)),
                        None
                    )

                    if existing_item:
                        if force_update or existing_item["auto_added"]:
                            # Оновлення існуючого запису
                            updated_metadata.append(update_metadata_fn(existing_item, directory, path))
                        else:
                            updated_metadata.append(existing_item)
                    else:
                        # Додавання нового запису
                        updated_metadata.append(create_metadata_fn(directory, path))

                # Якщо є файли (для фільмів)
                for file in files:
                    path = os.path.join(root, file)
                    if os.path.isfile(path) and not any(os.path.normpath(item["path"]) == os.path.normpath(path) for item in existing_metadata):
                        updated_metadata.append(create_metadata_fn(file, path))

                break  # Розглядаємо тільки верхній рівень директорій

    return updated_metadata
