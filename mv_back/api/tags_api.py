import json

from mv_back.db.utils import get_db, db_connection
from mv_back.db.tags_db import *


# --------------------------------------------------------------
# GETs

def get_all_tags_route_handler():
    try:
        with db_connection() as cursor:
            tags = select_tag_list(cursor)
            return {"tags": tags}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_tags_by_media_id_route_handler(media_id):
    try:
        with db_connection() as cursor:
            tags = select_tags_by_media_id(cursor, media_id)
            if not tags:
                return {"error": "No tags found for this media", 'id': media_id}, 404
            return {"data": tags}, 200
    except Exception as e:
        return {"error": str(e)}, 500


# --------------------------------------------------------------
# POSTs

def add_tag_to_list_route_handler(data):
    try:
        tag_value = data.get('tag') if data else None
        if not tag_value:
            return {"error": "Tag value is required"}, 400
        
        with db_connection(commit=True) as cursor:
            # Перевіряємо чи тег вже існує
            existing_tag = select_tag_by_name(cursor, tag_value)
            if existing_tag:
                return {"error": "Tag already exists", 'tag': tag_value}, 400
            
            # Додаємо новий тег
            rows_inserted = insert_Tag_to_db(cursor, tag_value)
            if rows_inserted == 0:
                return {"error": "Failed to add tag", 'tag': tag_value}, 500
            
            return {"message": "Tag added successfully", 'tag': tag_value}, 200
            
    except Exception as e:
        return {"error": str(e)}, 500

def add_tag_to_media_route_handler(media_id, data):
    try:
        tag_id = data.get('tag_id') if data else None
        if not tag_id:
            return {"error": "Tag ID is required", 'media_id': media_id}, 400
        
        with db_connection(commit=True) as cursor:
            success = insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id)
            if not success:
                return {"error": "Tag already associated with media", 'media_id': media_id, 'tag_id': tag_id}, 400
            
            return {"message": "Tag associated with media successfully", 'media_id': media_id, 'tag_id': tag_id}, 200
            
    except Exception as e:
        return {"error": str(e), 'media_id': media_id}, 500

def add_tag_to_list_of_media_route_handler(data):
    try:
        media_ids = data.get('media_ids') if data else None
        tag_id = data.get('tag_id') if data else None
        
        if not media_ids or not isinstance(media_ids, list):
            return {"error": "A list of media IDs is required"}, 400
        if not tag_id:
            return {"error": "Tag ID is required"}, 400
        
        with db_connection(commit=True) as cursor:
            rows_updated = insert_Xref_Tag2Media_bulk_to_db(cursor, media_ids, tag_id)
            if rows_updated == 0:
                return {"error": "Tag already associated with all specified media", 'tag_id': tag_id}, 400
            
            return {"message": f"Tag associated with {rows_updated} media items successfully", 'tag_id': tag_id, 'updated_count': rows_updated}, 200
            
    except Exception as e:
        return {"error": str(e)}, 500

def remove_tag_from_media_route_handler(media_id, data):
    try:
        tag_id = data.get('tag_id') if data else None
        if not tag_id:
            return {"error": "Tag ID is required", 'media_id': media_id}, 400
        
        with db_connection(commit=True) as cursor:
            # Перевіряємо чи існує тег
            tag = select_tag_by_id(cursor, tag_id)
            if not tag:
                return {"error": "Tag not found", 'tag_id': tag_id}, 404
            
            # Видаляємо зв'язок
            success = delete_tag_from_media(cursor, tag_id, media_id)
            if not success:
                return {"error": "Tag not associated with media", 'media_id': media_id, 'tag_id': tag_id}, 400
            
            return {"message": "Tag removed from media successfully", 'media_id': media_id, 'tag_id': tag_id}, 200
            
    except Exception as e:
        return {"error": str(e), 'media_id': media_id}, 500
