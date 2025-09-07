import os
import json
import pyodbc
from tqdm import tqdm
from datetime import datetime
from natsort import natsorted
from translitua import translit, UkrainianKMU

from ..metadata import load_metadata
from ..config import *

def formate_id(cursor, title, table, tries=0):
    base_id = translit(title, table=UkrainianKMU).replace(" ", "_").lower() + ("_(" + str(tries) + ")" if tries > 0 else "")
    cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (base_id,))
    if cursor.fetchone() is None:
        return base_id
    elif tries < 10:
        tries += 1
        return formate_id(cursor, title, table, tries)

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

def insert_to_Media_table(cursor, path):
    title = os.path.basename(path)
    id = formate_id(cursor, title, "Media")
    query = '''
        INSERT INTO Media (id, title, path, crD) VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (id, title, path, datetime.now()))
    return id

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

def insert_to_Series_table(cursor, media_id):
    query = '''
        INSERT INTO Series (media_id) VALUES (?);
    '''
    cursor.execute(query, (media_id))
    return media_id

def insert_to_Season_table(cursor, series_id, season_number, path):
    season_title = os.path.basename(path)
    season_id = formate_id(cursor, season_title, "Season") + "_s" + str(season_number)
    query = '''
        INSERT INTO Season (id, series_id, season_number, title, path) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (season_id, series_id, season_number, season_title, path))
    return season_id

def insert_to_Episode_table(cursor, season_id, episode_number, path):
    title = os.path.splitext(os.path.basename(path))[0]
    episode_id = season_id + "_e" + str(episode_number)
    query = '''
        INSERT INTO Episode (id, season_id, episode_number, title, file_path) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (episode_id, season_id, episode_number, title, path))
    return episode_id

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

def insert_movies_to_db(cursor):
    paths = os_get_all_items_paths(MOVIES_PATHS)
    for path in tqdm(paths, desc="Inserting movies to DB"):
        insert_movie_collection_to_db(cursor, path)
    return

def insert_serie_to_db(cursor, path):
    # insert into Media table
    media_id = insert_to_Media_table(cursor, path)
    
    # insert into Series table
    series_id = insert_to_Series_table(cursor, media_id)
    
    # insert Season into Season table
    seasons = natsorted(os.listdir(path))
    for season_index, season in enumerate(seasons, start=1):
        season_path = os.path.join(path, season)
        if os.path.isdir(season_path):
            season_id = insert_to_Season_table(cursor, series_id, season_index, season_path)
            
            # insert Episodes into Episode table
            for episode_index, episode in enumerate(natsorted(os.listdir(season_path)), start=1):
                episode_path = os.path.join(season_path, episode)
                if os.path.isfile(episode_path) and episode.lower().endswith(('.mp4', '.mkv', '.avi')):
                    episode_id = insert_to_Episode_table(cursor, season_id, episode_index, episode_path)
    cursor.commit()
    return media_id

def insert_series_to_db(cursor):
    paths = os_get_all_items_paths(SERIES_PATHS)
    for path in tqdm(paths, desc="Inserting series to DB"):
        insert_serie_to_db(cursor, path)
    return

if __name__ == "__main__":
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    insert_series_to_db(cursor)
    