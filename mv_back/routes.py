import json
import uuid
from flask import jsonify, request, send_file, Response, g
import os
from metadata import load_metadata, save_metadata, auto_add_metadata, find_metadata_item, update_paths_only
from analyze_video import analyze_video, clear_analysis_cache
from new_metadata import *
from thumbnails import find_first_video_in_directory, get_or_create_thumbnail
from config import *
from datetime import datetime
import mimetypes
import subprocess
from concurrent.futures import ThreadPoolExecutor
import pyodbc

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

def error_response(message, status=400):
    return jsonify({"status": "error", "message": message}), status

def register_routes(app):
    
    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    @app.route('/api/metadata/tags', methods=['GET'])
    def get_all_tags():
        """
        Повертає всі наявні теги без повторів.

        Returns:
            Response: Список унікальних тегів.
        """
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        tags = set()
        for category in ["series", "movies", "online_series"]:
            for item in metadata.get(category, []):
                item_tags = item.get("tags", [])
                tags.update(item_tags)

        return jsonify({"status": "success", "tags": list(tags)}), 200
    
    @app.route('/api/metadata/add_tag', methods=['POST'])
    def add_tag():
        """
        Додає новий тег до масиву тегів для вибраного масиву фільмів/серіалів за їх ідентифікаторами.

        Body Parameters:
            ids (list): Список ідентифікаторів фільмів/серіалів.
            tag (str): Новий тег, який потрібно додати.

        Returns:
            Response: Статус додавання тегу.
        """
        data = request.json
        ids = data.get('ids')
        new_tag = data.get('tag')

        if not ids or not new_tag:
            return error_response("Fields `ids` and `tag` are required", 400)

        # Завантаження метаданих
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        updated = False
        for category in ["series", "movies"]:
            for item in metadata.get(category, []):
                if item.get("id") in ids:
                    if "tags" not in item:
                        item["tags"] = []
                    if new_tag not in item["tags"]:
                        item["tags"].append(new_tag)
                        item["last_modified"] = datetime.now().isoformat()
                        item["auto_added"] = False
                        updated = True

        if not updated:
            return error_response("No items were updated", 404)

        # Збереження метаданих
        try:
            save_metadata(metadata)
        except Exception as e:
            return error_response(f"Failed to save metadata: {str(e)}", 500)

        return jsonify({"status": "success", "message": "Tag added successfully"}), 200
    
    @app.route('/api/metadata/online_series', methods=['POST'])
    def add_online_series():
        """
        Додає новий онлайн-серіал до метаданих.

        Body Parameters:
            title (str): Назва серіалу.
            image_url (str): URL зображення або локальний шлях.
            seasons (list): Список сезонів із епізодами та їх URL.

        Returns:
            Response: Статус додавання.
        """
        data = request.json
        title = data.get('title')
        image_url = data.get('image_url')  # Додано нове поле
        seasons = data.get('seasons')

        if not title or not seasons:
            return error_response("Fields `title` and `seasons` are required", 400)

        # Завантаження метаданих
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        new_series = {
            "id": str(uuid.uuid4()),
            "title": title,
            "image_url": image_url,  # Додаємо поле image_url
            "auto_added": True,
            "last_modified": datetime.now().isoformat(),
            "type": "online_series",
            "seasons": seasons
        }
        metadata.setdefault("online_series", []).append(new_series)

        # Збереження метаданих
        try:
            save_metadata(metadata)
        except Exception as e:
            return error_response(f"Failed to save metadata: {str(e)}", 500)

        return jsonify({"status": "success", "message": "Online series added successfully"}), 201

    @app.route('/api/metadata/online_time_to_skip', methods=['GET'])
    def get_online_time_to_skip():
        """
        Повертає параметр `timeToSkip` для онлайн-епізоду.

        Query Parameters:
            id (str): Унікальний ідентифікатор серіалу.
            season (str): Назва сезону.
            episode (str): Назва епізоду.

        Returns:
            Response: Параметр `timeToSkip` або помилка.
        """
        series_id = request.args.get('id')  # Унікальний ID онлайн-серіалу
        season_title = request.args.get('season')  # Назва сезону
        episode_title = request.args.get('episode')  # Назва епізоду

        if not series_id or not season_title or not episode_title:
            return error_response("Fields `id`, `season`, and `episode` are required", 400)

        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        for online_series in metadata.get("online_series", []):
            if online_series.get("id") == series_id:
                for season in online_series.get("seasons", []):
                    if season.get("title") == season_title:
                        for episode in season.get("episodes", []):
                            if episode.get("title") == episode_title:
                                time_to_skip = episode.get("timeToSkip", [])
                                return jsonify({"status": "success", "timeToSkip": time_to_skip}), 200

        return error_response("Episode not found in metadata", 404)

    @app.route('/api/metadata/time_to_skip', methods=['GET'])
    def get_time_to_skip():
        """
        Повертає параметр `timeToSkip` для вказаного файлу сезону.

        Query Parameters:
            path (str): Шлях до сезону.
            name (str): Назва файлу у сезоні.

        Returns:
            Response: Параметр `timeToSkip` або помилка.
        """
        data = request.args
        season_path = data.get('path')  # Шлях до сезону
        file_name = data.get('name')     # Назва файлу

        if not season_path or not file_name:
            return error_response("Fields `path` and `name` are required", 400)

        # Завантаження метаданих
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        # Пошук сезону і файлу
        for series in metadata.get("series", []):
            for season in series.get("seasons", []):
                if os.path.normpath(season.get("path")) == os.path.normpath(season_path):
                    for file in season.get("files", []):
                        if file.get("name") == file_name:
                            time_to_skip = file.get("timeToSkip", [])
                            return jsonify({"status": "success", "timeToSkip": time_to_skip}), 200

        return error_response("File not found in metadata", 404)

    @app.route('/api/metadata/time_to_skip', methods=['POST'])
    def update_time_to_skip():
        """
        Оновлює параметр `timeToSkip` у метаданих для вказаного файлу серіалу.

        Body Parameters:
            path (str): Шлях до сезону.
            name (str): Назва файлу у сезоні.
            timeToSkip (list): Масив таймкодів для пропуску у форматі [{"start": <start>, "end": <end>}].

        Returns:
            Response: Статус оновлення метаданих.
        """
        data = request.json
        season_path = data.get('path')  # Шлях до сезону
        file_name = data.get('name')    # Назва файлу
        time_to_skip = data.get('timeToSkip')  # Таймкоди для пропуску

        if not season_path or not file_name or not time_to_skip:
            return error_response("Fields `path`, `name`, and `timeToSkip` are required", 400)

        # Завантаження метаданих
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        # Оновлення метаданих
        updated = False
        for series in metadata.get("series", []):
            for season in series.get("seasons", []):
                if os.path.normpath(season.get("path")) == os.path.normpath(season_path):
                    for file in season.get("files", []):
                        if file.get("name") == file_name:
                            file["timeToSkip"] = time_to_skip
                            series["auto_added"] = False  # Позначення серіалу як вручну зміненого
                            updated = True
                            break

        if not updated:
            return error_response("File not found in metadata", 404)

        # Збереження метаданих
        try:
            save_metadata(metadata)
        except Exception as e:
            return error_response(f"Failed to update metadata: {str(e)}", 500)

        return jsonify({"status": "success", "message": "Metadata updated successfully"}), 200
    
    @app.route('/api/metadata/time_to_skip/bulk', methods=['POST'])
    def bulk_update_time_to_skip():
        """
        Додає однаковий `timeToSkip` для всіх епізодів у сезоні після вказаного (включно).

        Body Parameters:
            path (str): Шлях до сезону.
            name (str): Назва файлу у сезоні, з якого почати оновлення.
            timeToSkip (list): Масив таймкодів для пропуску у форматі [{"start": <start>, "end": <end>}].

        Returns:
            Response: Статус оновлення метаданих.
        """
        data = request.json
        season_path = data.get('path')  # Шлях до сезону
        start_file_name = data.get('name')  # Назва файлу, з якого починається оновлення
        time_to_skip = data.get('timeToSkip')  # Таймкоди для пропуску

        if not season_path or not start_file_name or not time_to_skip:
            return error_response("Fields `path`, `name`, and `timeToSkip` are required", 400)

        # Завантаження метаданих
        try:
            metadata = load_metadata()
        except Exception as e:
            return error_response(f"Failed to load metadata: {str(e)}", 500)

        # Оновлення timeToSkip для файлів
        updated = False
        for series in metadata.get("series", []):
            for season in series.get("seasons", []):
                if os.path.normpath(season.get("path")) == os.path.normpath(season_path):
                    start_updating = False
                    for file in season.get("files", []):
                        if file.get("name") == start_file_name:
                            start_updating = True

                        if start_updating:
                            file["timeToSkip"] = time_to_skip
                            updated = True

                    if updated:
                        series["auto_added"] = False  # Позначаємо серіал як вручну змінений
                        break

        if not updated:
            return error_response("File not found in metadata or no updates made", 404)

        # Збереження метаданих
        try:
            save_metadata(metadata)
        except Exception as e:
            return error_response(f"Failed to save metadata: {str(e)}", 500)

        return jsonify({"status": "success", "message": "Bulk update completed successfully"}), 200

    @app.route('/api/metadata/item/<string:item_id>', methods=['GET'])
    def get_metadata_by_id(item_id):
        metadata = load_metadata()
        item, _ = find_metadata_item(metadata, item_id=item_id)
        if item:
            return jsonify({"status": "success", "item": item})
        return error_response("Item not found")

    @app.route('/api/metadata/item', methods=['GET'])
    def get_metadata_item():
        path = request.args.get('path')
        if not path:
            return error_response("Path is required")

        metadata = load_metadata()
        for category in ["series", "movies"]:
            for item in metadata[category]:
                if os.path.normpath(item["path"]) == os.path.normpath(path):
                    return jsonify({"status": "success", "item": item})

        return error_response("Item not found")

    @app.route('/api/metadata/search', methods=['GET'])
    def search_metadata():
        query = request.args.get('query', "").lower()
        metadata = load_metadata()
        results = {"series": [], "movies": []}

        for category in ["series", "movies"]:
            for item in metadata[category]:
                if query in item.get("title", "").lower() or query in " ".join(item.get("tags", [])).lower():
                    results[category].append(item)

        return jsonify({"status": "success", "results": results})

    @app.route('/api/metadata/item/<string:item_id>', methods=['PUT'])
    def update_metadata_by_id(item_id):
        data = request.json
        metadata = load_metadata()
        item, category = find_metadata_item(metadata, item_id=item_id)

        if item:
            item.update(data)
            item["last_modified"] = datetime.now().isoformat()
            save_metadata(metadata)
            return jsonify({"status": "success", "message": "Metadata updated", "item": item})

        return error_response("Item not found")

    @app.route('/api/metadata/item/<string:item_id>/update-paths', methods=['POST'])
    def update_item_paths(item_id):
        """
        Оновлює тільки шляхи до файлів для вказаного елемента.
        
        Parameters:
            item_id (str): Ідентифікатор елемента

        Returns:
            Response: Статус оновлення шляхів
        """
        metadata = load_metadata()
        success, message = update_paths_only(metadata, item_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": message
            }), 200
        else:
            return error_response(message, 404)

    # API endpoint to get metadata
    @app.route('/api/metadata', methods=['GET'])
    def get_metadata():
        conn = get_db()
        if not conn:
            return error_response("Database connection error", 500)
        success, media_list, code = load_media(conn)
        if success is True:
            metadata = {
                "series": [],
                "movies": [],
                "online_series": []
            }
            for media in media_list:
                if media["type"] == "series":
                    metadata["series"].append(media)
                elif media["type"] == "collection":
                    metadata["movies"].append(media)
                elif media["type"] == "online_series":
                    metadata["online_series"].append(media)
            return jsonify(metadata), 200
        elif success is False:
            return error_response("No media found", 404)
        else:
            return error_response(success, code)

    # API endpoint to delete metadata
    @app.post("/api/metadata/delete")
    def delete_metadata_route():
        data = request.json
        media_id = data.get("id")

        if not media_id:
            return error_response("Field `id` is required", 400)

        conn = get_db()
        if not conn:
            return error_response("Database connection error", 500)
        success, code = delete_metadata(conn, media_id)

        if success is True:
            return jsonify({"status": "success", "message": "Metadata deleted"}), code
        elif success is False:
            return error_response("Metadata not found", code)
        else:
            return error_response(success, code)

    @app.route('/api/thumbnail', methods=['GET'])
    def get_thumbnail():
        folder_or_file_path = request.args.get('folder_name')
        if not folder_or_file_path:
            return error_response("Invalid folder or file path")

        if os.path.isfile(folder_or_file_path):
            # Якщо це файл, безпосередньо викликаємо get_or_create_thumbnail
            video_path = folder_or_file_path
            thumbnail_path = get_or_create_thumbnail(video_path)
        else:
            # Якщо це папка, знаходимо перший відеофайл у папці
            video_path = find_first_video_in_directory(folder_or_file_path)
            if not video_path:
                return error_response("No video files found in directory")
            thumbnail_path = get_or_create_thumbnail(folder_or_file_path)

        # Виклик функції get_or_create_thumbnail для створення мініатюри, якщо вона не існує
        
        if thumbnail_path:
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            return jsonify({"error": "No thumbnail could be created"}), 404

    @app.route('/api/video/audio-tracks', methods=['GET'])
    def get_audio_tracks():
        """
        Повертає список доступних аудіодоріжок для відеофайлу.

        Query Parameters:
            path (str): Шлях до відеофайлу.

        Returns:
            Response: Список аудіодоріжок або помилка.
        """
        video_path = request.args.get('path')
        if not video_path or not os.path.exists(video_path):
            return error_response("File not found", 404)

        try:
            command = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-select_streams", "a",
                video_path
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            audio_info = json.loads(result.stdout)
            
            tracks = []
            for idx, stream in enumerate(audio_info.get('streams', [])):
                tracks.append({
                    'index': stream.get('index'),
                    'codec': stream.get('codec_name'),
                    'language': stream.get('tags', {}).get('language'),
                    'title': stream.get('tags', {}).get('title'),
                })
            
            return jsonify({
                "status": "success",
                "tracks": tracks
            }), 200
            
        except Exception as e:
            return error_response(f"Failed to get audio tracks: {str(e)}", 500)

    @app.route('/api/metadata/audio-track', methods=['POST'])
    def save_audio_track():
        """
        Зберігає вибрану аудіодоріжку в метаданих.

        Body Parameters:
            path (str): Шлях до сезону
            name (str): Назва файлу
            trackIndex (int): Індекс вибраної аудіодоріжки

        Returns:
            Response: Статус збереження
        """
        data = request.json
        season_path = data.get('path')
        file_name = data.get('name')
        track_index = data.get('trackIndex')

        if not all([season_path, file_name, track_index is not None]):
            return error_response("Missing required fields", 400)

        metadata = load_metadata()
        updated = False

        for series in metadata.get("series", []):
            for season in series.get("seasons", []):
                if os.path.normpath(season.get("path")) == os.path.normpath(season_path):
                    for file in season.get("files", []):
                        if file.get("name") == file_name:
                            file["preferredAudioTrack"] = track_index
                            series["auto_added"] = False
                            updated = True
                            break

        if updated:
            save_metadata(metadata)
            return jsonify({"status": "success", "message": "Audio track preference saved"}), 200
        
        return error_response("File not found in metadata", 404)