import json

from mv_back.thumbnails import get_or_create_thumbnail
from mv_back.db.media_db import *
from mv_back.db.tags_db import *

def get_media_with_tags_by_id(cursor, media_id):
    media = select_media_by_id(cursor, media_id)
    if not media:
        return {"error": "Media not found", 'status_code': 404, 'id': media_id}
    tags = select_tags_by_media_id(cursor, media_id)
    
    data = {
        'id': media[0],
        'title': media[1],
        'tags': tags,
        'img_path': get_or_create_thumbnail(media[2]),
        'path': media[2],
        'auto_added': media[3],
        'crD': media[4],
        'modD': media[5],
        'delD': media[6]
    }
    return {"data": data, 'status_code': 200}

def get_all_media_with_tags(cursor):
    all_media = select_all_media_with_tags(cursor)
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
    return {"data": formatted_media, 'status_code': 200}

def update_media(cursor, media_id, new_media):
    existing_media = select_media_by_id(cursor, media_id)
    if not existing_media:
        return {"error": "Media not found", 'status_code': 404, 'id': media_id}
    
    rows_updated = update_media_by_id(cursor, media_id, new_media)
    if rows_updated == 0:
        return {"error": "No changes made", 'status_code': 400, 'id': media_id}
    
    return {"message": "Media updated successfully", 'status_code': 200, 'id': media_id}