import os
import json
from natsort import natsorted
from datetime import datetime

from mv_back.db.utils import *
from mv_back.db.media_db import *
from mv_back.thumbnails import get_or_create_thumbnail


# --------------------------------------------------------------
# Formatters (допоміжні функції для форматування)

def format_movie_collection(collection):
    """Форматує movie collection record у словник"""
    if not collection:
        return None
    return {
        'id': collection[0],
        'title': collection[1],
        'path': collection[2],
        'auto_added': collection[3],
        'crD': collection[4],
        'modD': collection[5],
        'delD': collection[6]
    }

def format_movie_item(item):
    """Форматує movie item record у словник"""
    if not item:
        return None
    return {
        'id': item[0],
        'primary_collection_id': item[1],
        'position': item[2],
        'title': item[3],
        'path': item[4]
    }

def format_movie_with_tags(movie):
    """Форматує movie з тегами у словник"""
    if not movie:
        return None
    
    tags = []
    if movie[7]:
        tags = [tag['value'] for tag in json.loads(movie[7])]
    
    return {
        'id': movie[0],
        'title': movie[1],
        'path': movie[2],
        'tags': tags,
        'img_path': get_or_create_thumbnail(movie[2]),
        'auto_added': movie[3],
        'crD': movie[4],
        'modD': movie[5],
        'delD': movie[6]
    }


#--------------------------------------------------------------
# INSERTs

def insert_to_Movie_table(cursor, media_id):
    query = '''
        INSERT INTO Movie (media_id) VALUES (?);
    '''
    cursor.execute(query, (media_id))
    return media_id

def insert_to_MovieItem_table(cursor, movie_id, position, path):
    title = os.path.splitext(os.path.basename(path))[0]
    item_id = formate_id(cursor, title, "MovieItem") + "_" + str(position)
    query = '''
        INSERT INTO MovieItem (id, primary_collection_id, position, title, path) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (item_id, movie_id, position, title, path))
    return item_id

def insert_movie_collection_to_db(cursor, path):
    
    # insert into Media table
    media_id = insert_to_Media_table(cursor, path)
    
    # insert into Movie table
    movie_id = insert_to_Movie_table(cursor, media_id)
    
    # insert MovieItems into MovieItem table
    collection_items = natsorted(os.listdir(path))
    for index, item in enumerate(collection_items, start=1):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mkv', '.avi')):
            item_id = insert_to_MovieItem_table(cursor, movie_id, index, item_path)
    cursor.commit()
    return media_id

#--------------------------------------------------------------
# SELECTs (тепер повертають відформатовані дані)

def select_all_movies_collections(cursor):
    query = '''
        SELECT Media.id, Media.title, Media.path, Media.auto_added, Media.crD, Media.modD, Media.delD
        FROM Movie
        INNER JOIN Media ON Movie.media_id = Media.id AND Media.delD IS NULL
        WHERE Movie.delD IS NULL;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return [format_movie_collection(row) for row in results] if results else []

def select_movie_collection_by_id(cursor, movie_id):
    """Отримує movie collection за ID"""
    collections = select_all_movies_collections(cursor)
    return next((col for col in collections if col['id'] == movie_id), None)
    
def select_movie_items_by_collection_id(cursor, movie_id):
    query = '''
        SELECT id, primary_collection_id, position, title, path 
        FROM MovieItem 
        WHERE primary_collection_id = ? AND delD IS NULL
        ORDER BY position;
    '''
    cursor.execute(query, (movie_id,))
    rows = cursor.fetchall()
    return [format_movie_item(row) for row in rows] if rows else []

def select_movie_item_by_id(cursor, item_id):
    query = '''
        SELECT id, primary_collection_id, position, title, path 
        FROM MovieItem 
        WHERE id = ? AND delD IS NULL;
    '''
    cursor.execute(query, (item_id,))
    row = cursor.fetchone()
    return format_movie_item(row)

def select_all_movies_with_tags(cursor):
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
        INNER JOIN Movie mv on mv.media_id = m.id AND mv.delD IS NULL
        WHERE m.delD IS NULL
        ORDER BY m.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return [format_movie_with_tags(row) for row in results] if results else []

#--------------------------------------------------------------
# UPDATEs

def update_movie_item_by_id_db(cursor, item_id, new_data):
    fields = []
    values = []
    for key, value in new_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    if not fields:
        return 0  # No valid fields to update
    values.append(item_id)
    currentdate = datetime.now()
    query = f'''
        UPDATE MovieItem
        SET {', '.join(fields)}, modD = {currentdate}
        WHERE id = ? AND delD IS NULL;
    '''
    cursor.execute(query, tuple(values))
    return cursor.rowcount

def update_movie_collection_by_id_db(cursor, movie_id, new_data):
    fields = []
    values = []
    for key, value in new_data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    if not fields:
        return 0  # No valid fields to update
    values.append(movie_id)
    currentdate = datetime.now()
    query = f'''
        UPDATE Media
        SET {', '.join(fields)}, modD = {currentdate}
        WHERE id = (SELECT media_id FROM Movie WHERE media_id = ? AND delD IS NULL);
    '''
    cursor.execute(query, tuple(values))
    return cursor.rowcount