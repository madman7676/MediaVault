import os
import json
import pyodbc
from tqdm import tqdm
from datetime import datetime
from natsort import natsorted
from translitua import translit, UkrainianKMU

from ..metadata import load_metadata
from ..config import *

def formate_id(title):
    return translit(title, table=UkrainianKMU).replace(" ", "_").lower()

def os_get_all_items_paths(paths):
    items = []
    for path in paths:
        if not os.path.exists(path):
            continue
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                items.append(item_path)
    return items

def insert_collection_to_db(cursor, path):
    
    # insert into Media table
    title = os.path.basename(path)
    id = formate_id(title)
    query = '''
        INSERT INTO Media (id, title, path, crD) VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (id, title, path, datetime.now()))
    
    # insert into Movie table
    query = '''
        INSERT INTO Movie (media_id) VALUES (?);
    '''
    cursor.execute(query, (id))
    
    # insert MovieItems into MovieItem table
    collection_items = natsorted(os.listdir(path))
    for index, item in enumerate(collection_items, start=1):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mkv', '.avi')):
            file_title = os.path.splitext(item)[0]
            file_id = formate_id(file_title) + "_" + str(index)
            file_query = '''
                INSERT INTO MovieItem (id, collection_id, position, title, path) VALUES (?, ?, ?, ?, ?);
            '''
            cursor.execute(file_query, (file_id, id, index, file_title, item_path))
    cursor.commit()
    return

def insert_movies_to_db(cursor):
    paths = os_get_all_items_paths(MOVIES_PATHS)
    for path in tqdm(paths, desc="Inserting movies to DB"):
        insert_collection_to_db(cursor, path)
    return

if __name__ == "__main__":
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.executemany
    insert_movies_to_db(cursor)
    print(os_get_all_items_paths(MOVIES_PATHS))