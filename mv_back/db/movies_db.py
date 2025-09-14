import os
from natsort import natsorted

from mv_back.db.utils import *
from mv_back.db.media_db import *


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
# SELECTs

def select_all_movies_collections(cursor):
    query = '''
        SELECT Media.id, Media.title, Media.path, Media.auto_added, Media.crD, Media.modD, Media.delD
        FROM Movie
        INNER JOIN Media ON Movie.media_id = Media.id AND Media.delD IS NULL
        WHERE Movie.delD IS NULL;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []
    
def select_movie_items_by_collection_id(cursor, movie_id):
    query = '''
        SELECT id, primary_collection_id, position, title, path 
        FROM MovieItem 
        WHERE primary_collection_id = ? AND delD IS NULL
        ORDER BY position;
    '''
    cursor.execute(query, (movie_id,))
    rows = cursor.fetchall()
    if rows:
        return rows
    else:
        return []

def select_movie_item_by_id(cursor, item_id):
    query = '''
        SELECT id, primary_collection_id, position, title, path 
        FROM MovieItem 
        WHERE id = ? AND delD IS NULL;
    '''
    cursor.execute(query, (item_id,))
    row = cursor.fetchone()
    if row:
        return row
    else:
        return None

#--------------------------------------------------------------
# UPDATEs

def update_movie_item_by_id(cursor, item_id, new_data):
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

def update_movie_collection_by_id(cursor, movie_id, new_data):
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