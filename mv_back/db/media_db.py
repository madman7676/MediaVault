import os
import json
from mv_back.db.utils import *
from mv_back.thumbnails import get_or_create_thumbnail
from datetime import datetime


# --------------------------------------------------------------
# Formatters (допоміжні функції для форматування)

def format_media(media):
    """Форматує media record у словник"""
    if not media:
        return None
    return {
        'id': media[0],
        'title': media[1],
        'path': media[2],
        'auto_added': media[3],
        'crD': media[4],
        'modD': media[5],
        'delD': media[6]
    }

def format_media_with_tags(media, tags=None):
    """Форматує media record з тегами у словник"""
    if not media:
        return None
    
    # Якщо це результат з select_all_media_with_tags (з JSON тегами)
    if len(media) == 8 and media[7] is not None:
        tags = []
        if media[7]:
            tags = [tag['value'] for tag in json.loads(media[7])]
    
    return {
        'id': media[0],
        'title': media[1],
        'tags': tags if tags is not None else [],
        'img_path': get_or_create_thumbnail(media[2]) if media[2] else None,
        'path': media[2],
        'auto_added': media[3],
        'crD': media[4],
        'modD': media[5],
        'delD': media[6]
    }


# --------------------------------------------------------------
# Inserts

def insert_to_Media_table(cursor, path):
    title = os.path.basename(path)
    id = formate_id(cursor, title, "Media")
    query = '''
        INSERT INTO Media (id, title, path, crD) VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (id, title, path, datetime.now()))
    return id


# --------------------------------------------------------------
# Selects (тепер повертають відформатовані дані)

def select_media_by_id(cursor, media_id):
    cursor.execute('SELECT * FROM Media WHERE id = ? AND delD IS NULL', (media_id,))
    result = cursor.fetchone()
    return format_media(result)

def select_all_media(cursor):
    cursor.execute('SELECT * FROM Media WHERE delD IS NULL ORDER BY title;')
    results = cursor.fetchall()
    return [format_media(row) for row in results] if results else []

def select_all_media_with_tags(cursor):
    query = '''
        SELECT m.id, m.title, m.[path], m.auto_added, m.crD, m.modD, m.delD,
            JSON_QUERY((
                SELECT tag.[name] AS [value]
                FROM Xref_Tag2Media ref
                left join Tag on tag.id = ref.tag_id AND tag.delD IS NULL
                WHERE ref.media_id = m.id AND ref.delD IS NULL
                FOR JSON PATH
            )) AS tags_json
        FROM Media m
        WHERE m.delD IS NULL
        ORDER BY m.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return [format_media_with_tags(row) for row in results] if results else []

# Нова функція для отримання медіа з тегами за ID
def select_media_with_tags_by_id(cursor, media_id):
    """Повертає media з тегами за ID"""
    from mv_back.db.tags_db import select_tags_by_media_id
    
    media = select_media_by_id(cursor, media_id)
    if not media:
        return None
    
    tags = select_tags_by_media_id(cursor, media_id)
    return format_media_with_tags([
        media['id'], media['title'], media['path'], 
        media['auto_added'], media['crD'], media['modD'], media['delD']
    ], tags)


# --------------------------------------------------------------
# Updates

def update_media_by_id(cursor, media_id, new_media):
    fields = []
    values = []
    for key, value in new_media.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(media_id)
    set_clause = ", ".join(fields)
    current_date = datetime.now()
    query = f"UPDATE Media SET {set_clause}, modD = {current_date} WHERE id = ? AND delD IS NULL"
    cursor.execute(query, values)
    return cursor.rowcount