import uuid
from flask import jsonify, request, send_file, Response
import os
from metadata import load_metadata, save_metadata, auto_add_metadata, find_metadata_item
from analyze_video import analyze_video, clear_analysis_cache
from thumbnails import find_first_video_in_directory, get_or_create_thumbnail
from config import THUMBNAILS_DIR, MOVIES_PATHS, SERIES_PATHS
from datetime import datetime
import mimetypes
import subprocess
from concurrent.futures import ThreadPoolExecutor

def convert_to_mp4(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error converting file: {result.stderr.decode('utf-8')}")
        return False
    return True

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

def error_response(message, status=400):
    return jsonify({"status": "error", "message": message}), status

def register_routes(app):
    
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
    
    @app.route('/api/analyze/clear_cache', methods=['POST'])
    def clear_cache_route():
        """
        Видаляє кешований результат аналізу для вказаного відеофайлу.

        Body Parameters:
            path (str): Шлях до відеофайлу.

        Returns:
            Response: Результат видалення кешу.
        """
        video_path = request.json.get('path')
        if not video_path:
            return error_response("Path parameter is required",400)

        try:
            clear_analysis_cache(video_path=video_path)
            return jsonify({"status": "success", "message": f"Cache cleared for file: {video_path}"}), 200
        except Exception as e:
            return error_response(f"Failed to clear cache for file {video_path}", 404)
            # error_response(f"Failed to clear cache for file {video_path}: {e}")
            # return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/analyze/video', methods=['GET'])
    def get_video_analysis():
        """
        Повертає результати аналізу для конкретного відео.

        Query Parameters:
            path (str): Шлях до відеофайлу.

        Returns:
            Response: Результати аналізу або помилка.
        """
        video_path = request.args.get('path')
        if not video_path or not os.path.exists(video_path):
            return error_response("File not found", 404)

        metadata = load_metadata()
        for series in metadata.get("series", []):
            for season in series.get("seasons", []):
                for file in season.get("files", []):
                    if os.path.normpath(os.path.join(season["path"], file["name"])) == os.path.normpath(video_path):
                        return jsonify({"status": "success", "recommendToSkip": file.get("recommendToSkip", [])})

        return error_response("Analysis not found", 404)

    @app.route('/api/analyze/series/<string:series_id>', methods=['POST'])
    def analyze_series(series_id):
        """
        Запускає аналіз для серіалу за його ідентифікатором з використанням паралельної обробки.

        Parameters:
            series_id (str): Унікальний ідентифікатор серіалу.

        Returns:
            Response: Статус запуску аналізу.
        """
        metadata = load_metadata()
        series, _ = find_metadata_item(metadata, item_id=series_id)

        if not series or series.get("type") != "series":
            return error_response("Series not found", 404)

        def process_video(file_info):
            video_path = os.path.join(file_info["season_path"], file_info["name"])
            analysis_result = analyze_video(video_path)
            file_info["file"]["recommendToSkip"] = analysis_result
            return {"file": file_info["name"], "recommendToSkip": analysis_result}

        files_to_analyze = []
        for season in series.get("seasons", []):
            for file in season.get("files", []):
                files_to_analyze.append({"season_path": season["path"], "name": file["name"], "file": file})

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_video, files_to_analyze))

        save_metadata(metadata)
        return jsonify({"status": "success", "results": results})
    
    @app.route('/api/analyze/file', methods=['POST'])
    def analyze_file():
        """
        Аналізує один відеофайл та повертає результати.

        Query Parameters:
            path (str): Шлях до відеофайлу.

        Returns:
            Response: Результати аналізу або повідомлення про помилку.
        """
        video_path = request.json.get('path')

        if not video_path or not os.path.exists(video_path):
            return jsonify({"status": "error", "message": "File not found or invalid path"}), 404

        try:
            results = analyze_video(video_path)
            return jsonify({"status": "success", "results": results})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/video', methods=['GET'])
    def serve_video_with_range():
        """
        Надає доступ до відеофайлу з підтримкою Range-запитів і потоковою передачею.

        Query Parameters:
            path (str): Шлях до відеофайлу.

        Returns:
            Response: Відеофайл або помилка.
        """
        video_path = request.args.get('path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({"status": "error", "message": "File not found"}), 404

        extension = os.path.splitext(video_path)[-1].lower()
        if extension == ".avi":
            # Конвертація AVI у MP4
            converted_path = video_path.replace(".avi", ".mp4")
            if not os.path.exists(converted_path):
                success = convert_to_mp4(video_path, converted_path)
                if not success:
                    return jsonify({"status": "error", "message": "Failed to convert file"}), 500
            video_path = converted_path
        
        # Визначення MIME-типу
        mime_type, _ = mimetypes.guess_type(video_path)
        mime_type = mime_type or "application/octet-stream"

        range_header = request.headers.get('Range', None)

        try:
            file_size = os.path.getsize(video_path)

            if range_header:
                # Обробка Range-запиту
                range_value = range_header.strip().split('=')[-1]
                start, end = range_value.split('-')
                start = int(start) if start else 0
                end = int(end) if end else file_size - 1
                length = end - start + 1

                with open(video_path, 'rb') as f:
                    f.seek(start)
                    data = f.read(length)

                headers = {
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                    'Content-Type': mime_type
                }

                return Response(data, status=206, headers=headers)

            # Потокова передача всього файлу без Range-запиту
            def generate():
                with open(video_path, 'rb') as f:
                    while chunk := f.read(8192):
                        yield chunk

            headers = {
                'Content-Length': str(file_size),
                'Content-Type': mime_type
            }

            return Response(generate(), headers=headers)
        except Exception as e:
            import traceback
            print("Error:", traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 500

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

    # API endpoint to get metadata
    @app.route('/api/metadata', methods=['GET'])
    def get_metadata():
        metadata = load_metadata()
        metadata = auto_add_metadata(metadata)
        save_metadata(metadata)
        return jsonify(metadata)

    # API endpoint to force update metadata
    @app.route('/api/metadata/force-update', methods=['POST'])
    def force_update_metadata():
        metadata = load_metadata()
        metadata = auto_add_metadata(metadata, force_update=True)
        save_metadata(metadata)
        return jsonify({"status": "success", "message": "Metadata forcibly updated"})

    # API endpoint to add or update metadata
    @app.route('/api/metadata/add', methods=['POST'])
    def add_metadata():
        data = request.json
        metadata = load_metadata()

        # Check if the item already exists in metadata
        for item in metadata["series"] + metadata["movies"]:
            if os.path.normpath(item["path"]) == os.path.normpath(data["path"]):
                item.update(data)
                item["auto_added"] = False
                item["last_modified"] = datetime.now().isoformat()
                save_metadata(metadata)
                return jsonify({"status": "success", "message": "Metadata updated"})

        # Add new metadata
        data["id"] = str(uuid.uuid4())
        data["auto_added"] = False
        data["last_modified"] = datetime.now().isoformat()
        category = "series" if "series" in data["tags"] else "movies"
        metadata[category].append(data)
        save_metadata(metadata)
        return jsonify({"status": "success", "message": "Metadata added"})

    # API endpoint to delete metadata
    @app.route('/api/metadata/delete', methods=['POST'])
    def delete_metadata():
        """
        Видаляє запис із метаданих для `series`, `movies` або `online_series`.

        Body Parameters:
            id (str): Унікальний ідентифікатор запису, який потрібно видалити.

        Returns:
            Response: Статус видалення.
        """
        data = request.json
        record_id = data.get("id")

        if not record_id:
            return error_response("Field `id` is required", 400)

        metadata = load_metadata()

        # Пошук і видалення запису
        for category in ["series", "movies", "online_series"]:
            for item in metadata.get(category, []):
                if item.get("id") == record_id:
                    metadata[category].remove(item)
                    save_metadata(metadata)
                    return jsonify({"status": "success", "message": "Metadata deleted"}), 200

        return error_response("Item not found", 404)

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
