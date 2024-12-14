from flask import jsonify, request, send_file
import os
from metadata import load_metadata, save_metadata, auto_add_metadata, get_or_create_thumbnail
from config import THUMBNAILS_DIR

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

def register_routes(app):
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
        metadata = load_metadata()

        # Remove the item
        for category in ["series", "movies"]:
            new_metadata = [item for item in metadata[category] if os.path.normpath(item["path"]) != os.path.normpath(data["path"])]
            if len(new_metadata) != len(metadata[category]):
                metadata[category] = new_metadata
                save_metadata(metadata)
                return jsonify({"status": "success", "message": "Metadata deleted"})

        return jsonify({"status": "error", "message": "Item not found"})
    
    @app.route('/api/thumbnail', methods=['GET'])
    def get_thumbnail():
        video_path = request.args.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Invalid video path"}), 400

        thumbnail_path = get_or_create_thumbnail(video_path)
        if thumbnail_path:
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            return jsonify({"error": "No thumbnail could be created"}), 404
