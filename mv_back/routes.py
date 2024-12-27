from flask import jsonify, request, send_file, Response
import os
from metadata import load_metadata, save_metadata, auto_add_metadata, find_metadata_item
from analyze_video import analyze_video, clear_analysis_cache
from thumbnails import get_or_create_thumbnail
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
        data = request.json
        if "path" not in data:
            return error_response("Path is required")

        metadata = load_metadata()
        _, category = find_metadata_item(metadata, path=data["path"])

        if category:
            # Видаляємо запис із відповідної категорії
            metadata[category] = [
                item for item in metadata[category]
                if os.path.normpath(item["path"]) != os.path.normpath(data["path"])
            ]
            save_metadata(metadata)
            return jsonify({"status": "success", "message": "Metadata deleted"})

        return error_response("Item not found")

    @app.route('/api/thumbnail', methods=['GET'])
    def get_thumbnail():
        video_path = request.args.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return error_response("Invalid video path")

        thumbnail_path = get_or_create_thumbnail(video_path)
        if thumbnail_path:
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            return jsonify({"error": "No thumbnail could be created"}), 404
