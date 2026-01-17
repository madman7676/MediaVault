import os
import json
from datetime import datetime

from mv_back.db.utils import *

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
    if tags is None and len(media) > 7:
        if media[7] and media[7] != None:
            tags = [tag['value'] for tag in json.loads(media[7])]
    
    return {
        'id': media[0],
        'title': media[1],
        'tags': tags,
        'path': media[2],
        'count': media[8] if len(media) > 8 else None,
        'type': media[9] if len(media) > 9 else None,
        'auto_added': media[3],
        'crD': media[4],
        'modD': media[5],
        'delD': media[6]
    }

def format_parent_media(media):
    """Форматує media record для списку батьківських медіа"""
    if not media:
        return None
    return {
        'id': media[0],
        'title': media[1],
        'type': media[2]
    }


# --------------------------------------------------------------
# Inserts

def insert_to_Media_table(cursor, path, title=''):
    if not title:
        title = os.path.basename(path.rstrip("/\\"))
    id = formate_id(cursor, title, "Media")
    query = '''
        INSERT INTO Media (id, title, path, crD) VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (id, title, path, datetime.now()))
    return id

# --------------------------------------------------------------
# Selects (тепер повертають відформатовані дані)

def select_media_by_id(cursor, media_id):
    
    query = '''
        SELECT 
            m.*,
            NULL as tags_json,
            COALESCE(
                (SELECT MAX(position) 
                FROM MovieItem mi 
                WHERE mi.primary_collection_id = m.id 
                AND mi.delD IS NULL),
                (SELECT MAX(season_number) 
                FROM Season s 
                WHERE s.primary_series_id = m.id 
                AND s.delD IS NULL),
                0
            ) AS [count],
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM MovieItem mi
                    WHERE mi.primary_collection_id = m.id 
                    AND mi.delD IS NULL
                ) THEN 'movie'
                WHEN EXISTS (
                    SELECT 1 
                    FROM Season s
                    WHERE s.primary_series_id = m.id 
                    AND s.delD IS NULL
                ) THEN 'series'
                ELSE 'unknown'
            END AS type
        FROM Media m
        WHERE m.id = ? AND m.delD IS NULL;
    '''
    
    cursor.execute(query, (media_id,))
    result = cursor.fetchone()
    return format_media_with_tags(result)

def select_all_media(cursor):
    cursor.execute('SELECT * FROM Media WHERE delD IS NULL ORDER BY title;')
    results = cursor.fetchall()
    return [format_media(row) for row in results] if results else []

def select_all_media_with_tags(cursor, tags=None, filter_mode='include'):
    """Повертає всі media з тегами, з можливістю фільтрації за тегами"""
    
    tags_condition = build_tag_filter(tags, filter_mode)
    query = f'''
        SELECT 
            m.*,
            JSON_QUERY((
                SELECT tag.[name] AS [value]
                FROM Xref_Tag2Media ref
                LEFT JOIN Tag 
                    ON tag.id = ref.tag_id 
                AND tag.delD IS NULL
                WHERE ref.media_id = m.id 
                AND ref.delD IS NULL
                FOR JSON PATH
            )) AS tags_json,
            COALESCE(
                (SELECT MAX(position) 
                FROM MovieItem mi 
                WHERE mi.primary_collection_id = m.id 
                AND mi.delD IS NULL),
                (SELECT MAX(season_number) 
                FROM Season s 
                WHERE s.primary_series_id = m.id 
                AND s.delD IS NULL),
                0
            ) AS [count],
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM MovieItem mi
                    WHERE mi.primary_collection_id = m.id 
                    AND mi.delD IS NULL
                ) THEN 'movie'
                WHEN EXISTS (
                    SELECT 1 
                    FROM Season s
                    WHERE s.primary_series_id = m.id 
                    AND s.delD IS NULL
                ) THEN 'series'
                ELSE 'unknown'
            END AS type
        FROM Media m
        WHERE m.delD IS NULL {tags_condition['query']}
        ORDER BY m.title;
    '''
    cursor.execute(query, tags_condition['params'])
    results = cursor.fetchall()
    return [format_media_with_tags(row) for row in results] if results else []

def select_all_media_parents(cursor):
    """Повертає всі media для списку пов'язаних при створенні нової частини/сезону"""
    query = '''
        SELECT m.id, m.title, 
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM MovieItem mi
                    WHERE mi.primary_collection_id = m.id 
                    AND mi.delD IS NULL
                ) THEN 'movie'
                WHEN EXISTS (
                    SELECT 1 
                    FROM Season s
                    WHERE s.primary_series_id = m.id 
                    AND s.delD IS NULL
                ) THEN 'series'
                ELSE 'unknown'
            END AS type
        FROM Media m
        WHERE m.delD IS NULL
        ORDER BY m.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return [format_parent_media(row) for row in results] if results else []

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