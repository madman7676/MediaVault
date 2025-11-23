from flask import g, request, Blueprint, jsonify, send_file

from mv_back.api.thumbnails_api import *

thumbnails = Blueprint("thumbnails", __name__, url_prefix="/api/thumbnail")

def error_response(message, status=400):
    return jsonify({"status": "error", "message": message}), status
   
# --------------------------------------------------------------
# GETs

@thumbnails.route('/api/thumbnail', methods=['GET'])
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