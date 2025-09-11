from mv_back.db.series_db import *
from mv_back.db.tags_db import select_tags_by_media_id
from mv_back.thumbnails import get_or_create_thumbnail


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
    cursor.execute('SELECT media_id FROM Series')
    series_ids = [row[0] for row in cursor.fetchall()]
    all_series = []
    for series_id in series_ids:
        series_info = get_serie_by_media_id(cursor, series_id)
        if 'data' in series_info:
            all_series.append(series_info['data'])
    return {"data": all_series, 'status_code': 200}
