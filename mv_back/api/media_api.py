from mv_back.db.utils import db_connection
from mv_back.db.media_db import *


# --------------------------------------------------------------
# GETs

def get_all_media_with_tags(tags=None, filter_mode='include'):
    try:
        with db_connection() as cursor:
            all_media = select_all_media_with_tags(cursor, tags, filter_mode)
            return  all_media, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_media_with_tags_by_id(media_id):
    try:
        with db_connection() as cursor:
            media_data = select_media_with_tags_by_id(cursor, media_id)
            if not media_data:
                return {"error": "Media not found", 'id': media_id}, 404
            
            return media_data, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_media_by_id(media_id):
    try:
        with db_connection() as cursor:
            media_data = select_media_by_id(cursor, media_id)
            if not media_data:
                return {"error": "Media not found", 'id': media_id}, 404
            
            return media_data, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_media_structure_perview(path):
    import os
    import json
    
    def build_tree(path):
        structure = {}
        files = []

        for entry in os.scandir(path):
            if entry.is_dir():
                # вкладена папка -> рекурсивно будуємо об’єкт
                structure[entry.name] = build_tree(entry.path)
            else:
                # файл -> додаємо в масив _files
                name, ext = os.path.splitext(entry.name)
                ext = ext.lstrip(".")
                files.append(f"{name}.{ext}" if ext else name)

        if files:
            structure["_files"] = sorted(files)

        return structure
    
    root_name = os.path.basename(path)
    return json.dumps({root_name: build_tree(path)}, indent=2, ensure_ascii=False), 200

# --------------------------------------------------------------
# UPDATEs

def update_media(media_id, new_media):
    try:
        with db_connection(commit=True) as cursor:
            existing_media = select_media_by_id(cursor, media_id)
            if not existing_media:
                return {"error": "Media not found", 'id': media_id}, 404
            
            rows_updated = update_media_by_id(cursor, media_id, new_media)
            if rows_updated == 0:
                return {"error": "No changes made", 'id': media_id}, 400
            
            return {"message": "Media updated successfully", 'id': media_id}, 200
    except Exception as e:
        return {"error": str(e)}, 500