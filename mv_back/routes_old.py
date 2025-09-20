import os
import json
import uuid
import mimetypes
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import jsonify, request, send_file, Response

from mv_back.config import THUMBNAILS_DIR
from mv_back.api.video_api import prepare_video_payload
from mv_back.routes.metadata_old_routes import get_metadata_route
from mv_back.thumbnails import find_first_video_in_directory, get_or_create_thumbnail
from mv_back.metadata import load_metadata, save_metadata, find_metadata_item, update_paths_only


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
        return get_metadata_route()

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
        
        
    @app.route('/api/video', methods=['GET'])
    def serve_video_with_range():
        video_path = request.args.get('path')
        range_header = request.headers.get('Range', None)

        result = prepare_video_payload(video_path, range_header)
        status = result.get('status_code', 500)

        if 'error' in result:
            return jsonify({"status": "error", "message": result['error']}), status

        payload = result['data']
        vpath = payload['video_path']
        mime = payload['mime_type']
        file_size = payload['file_size']
        r = payload['range']

        try:
            if r:
                start = r['start']
                end = r['end']
                length = r['length']
                with open(vpath, 'rb') as f:
                    f.seek(start)
                    data = f.read(length)

                headers = {
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                    'Content-Type': mime
                }
                return Response(data, status=206, headers=headers)

            # stream whole file
            def generate():
                with open(vpath, 'rb') as f:
                    while chunk := f.read(8192):
                        yield chunk

            headers = {
                'Content-Length': str(file_size),
                'Content-Type': mime
            }
            return Response(generate(), headers=headers)
        except Exception as e:
            import traceback
            print("Error:", traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 500
