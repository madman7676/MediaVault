import os
from natsort import natsorted

from mv_back.db.utils import *
from mv_back.db.media_db import *


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
        INSERT INTO MovieItem (id, collection_id, position, title, path) VALUES (?, ?, ?, ?, ?);
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