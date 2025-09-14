import json

from mv_back.db.series_db import *
from mv_back.db.tags_db import select_tags_by_media_id
from mv_back.thumbnails import get_or_create_thumbnail


# --------------------------------------------------------------
# GETs

def get_serie_by_media_id(cursor, media_id):
    serie = select_serie_by_id(cursor, media_id)
    if not serie:
        return {"error": "Series not found", 'status_code': 404, 'id': media_id}
    tags = select_tags_by_media_id(cursor, media_id)
    data = {
        'id': serie[0],
        'title': serie[1],
        'tags': tags,
        'img_path': get_or_create_thumbnail(serie[2]),
        'path': serie[2],
        'auto_added': serie[3],
        'crD': serie[4],
        'modD': serie[5],
        'delD': serie[6]
    }
    return {"data": data, 'status_code': 200}

def get_all_series(cursor):
    series = select_all_series(cursor)
    data = []
    for serie in series:
        data.append({
            'id': serie[0],
            'title': serie[1],
            'img_path': get_or_create_thumbnail(serie[2]),
            'path': serie[2],
            'auto_added': serie[3],
            'crD': serie[4],
            'modD': serie[5],
            'delD': serie[6]
        })
    return {"data": data, 'status_code': 200}

def get_all_series_with_tags(cursor):
    series = select_all_series_with_tags(cursor)
    if series is None:
        return {"error": "No series found", 'status_code': 404}
    data = []
    for serie in series:
        tags = []
        if serie[7]:
            tags = [tag['value'] for tag in json.loads(serie[7])]
        data.append({
            'id': serie[0],
            'title': serie[1],
            'tags': tags,
            'img_path': get_or_create_thumbnail(serie[2]),
            'path': serie[2],
            'auto_added': serie[3],
            'crD': serie[4],
            'modD': serie[5],
            'delD': serie[6]
        })
    return {"data": data, 'status_code': 200}