import json

from mv_back.db.utils import db_connection
from mv_back.thumbnails import get_or_create_thumbnail
from mv_back.db.media_db import *
from mv_back.db.tags_db import *


# --------------------------------------------------------------
# GETs

def get_media_with_tags_by_id(media_id):
    try:
        with db_connection() as cursor:
            media = select_media_by_id(cursor, media_id)
            if not media:
                return {"error": "Media not found", 'id': media_id}, 404
            
            tags = select_tags_by_media_id(cursor, media_id)
            
            data = {
                'id': media[0],
                'title': media[1],
                'tags': tags,
                'img_path': get_or_create_thumbnail(media[2]) if media[2] else None,
                'path': media[2],
                'auto_added': media[3],
                'crD': media[4],
                'modD': media[5],
                'delD': media[6]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_media_with_tags():
    try:
        with db_connection() as cursor:
            all_media = select_all_media_with_tags(cursor)
            if not all_media:
                return {"data": []}, 200
            
            formatted_media = []
            for media in all_media:
                tags = []
                if media[7]:
                    tags = [tag['value'] for tag in json.loads(media[7])]
                formatted_media.append({
                    'id': media[0],
                    'title': media[1],
                    'tags': tags,
                    'img_path': get_or_create_thumbnail(media[2]),
                    'path': media[2],
                    'auto_added': media[3],
                    'crD': media[4],
                    'modD': media[5],
                    'delD': media[6]
                })
            return {"data": formatted_media}, 200
    except Exception as e:
        return {"error": str(e)}, 500


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