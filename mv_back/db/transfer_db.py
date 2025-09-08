import os
import json
import uuid
import pyodbc
import jmespath
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

def insert_SkipSet_to_db(cursor, episode_id, source, name='Default', priority=0, is_active=1):
    cursor.execute('SELECT id FROM SkipSet WHERE episode_id = ? AND source = ?', (episode_id, source))
    if cursor.fetchone() is not None:
        print(f"SkipSet for episode_id '{episode_id}' with source '{source}' already exists in DB. Skipping...")
        return None
    
    skipSet_id = formate_id(cursor, name+'-'+episode_id+'-'+source, "SkipSet")    
    query = '''
        INSERT INTO SkipSet (id, episode_id, name, source, priority, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipSet_id, episode_id, name, source, priority, is_active, datetime.now()))
    return skipSet_id

def insert_SkipRange_to_db(cursor, skipset_id, start, end, label='NULL'):
    skipRange_id = str(uuid.uuid4())
    query = '''
        INSERT INTO SkipRange (id, skipset_id, start_time_ms, end_time_ms, label) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipRange_id, skipset_id, start, end, label))
    return skipRange_id

def transfer_timeToSkip_from_metadata():    
    metadata = load_metadata()
    
    jmesstr = r'series[].seasons[].files[?timeToSkip].{name: name, timeToSkip: timeToSkip}[]'
    timeToSkipSets = jmespath.search(jmesstr, metadata)
    
    for item in tqdm(timeToSkipSets, desc="Transferring timeToSkip to DB"):
        episode_name = os.path.splitext(item['name'])[0]
        timeToSkip = item['timeToSkip']
        
        # Find episode_id in DB
        cursor.execute('SELECT id FROM Episode WHERE title = ?', (episode_name,))
        result = cursor.fetchone()
        if result is None:
            print(f"Episode '{episode_name}' not found in DB. Skipping...")
            continue
        episode_id = result[0]
        
        # Insert SkipSet
        skipset_id = insert_SkipSet_to_db(cursor, episode_id, source='METADATA', name='Default')
        if skipset_id is None:
            continue
        # Insert SkipRanges
        for skip in timeToSkip:
            if not skip:
                print(f"Empty skip range in episode '{episode_name}'. Skipping...")
                continue
            start = skip.get('start', 'NULL')
            end = skip.get('end', 'NULL')
            skipRange_id = insert_SkipRange_to_db(cursor, skipset_id, start, end, label='NULL')
    
    cursor.commit()
    return

def insert_Tag_to_db(cursor, name):
    cursor.execute('SELECT id FROM Tag WHERE name = ?', (name,))
    if cursor.fetchone() is not None:
        print(f"Tag '{name}' already exists in DB. Skipping...")
        return cursor.fetchone()[0]
    
    id = formate_id(cursor, name, "Tag")
    query = '''
        INSERT INTO Tag (id, name) VALUES (?, ?);
    '''
    cursor.execute(query, (id, name))
    return id

def insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id):
    cursor.execute('SELECT * FROM Xref_Tag2Media WHERE media_id = ? AND tag_id = ?', (media_id, tag_id))
    if cursor.fetchone() is not None:
        print(f"Xref_Tag2Media for media_id '{media_id}' and tag_id '{tag_id}' already exists in DB. Skipping...")
        return False
    
    query = '''
        INSERT INTO Xref_Tag2Media (media_id, tag_id) VALUES (?, ?);
    '''
    cursor.execute(query, (media_id, tag_id))
    return True
    

def transfer_tags_from_metadata():
    metadata = load_metadata()
    
    jmesstr = r'*[?tags].{tags:tags[], title:title}[]'
    tagSets = jmespath.search(jmesstr, metadata)
    
    cursor.execute('SELECT * FROM Tag')
    
    tagsList = {row[1]:row[0] for row in cursor.fetchall()}
    
    for item in tqdm(tagSets, desc="Transferring tags to DB"):
        title = item['title']
        tags = item['tags']
        
        # Find media_id in DB
        cursor.execute('SELECT id FROM Media WHERE title = ?', (title,))
        result = cursor.fetchone()
        if result is None:
            print(f"Media '{title}' not found in DB. Skipping...")
            continue
        media_id = result[0]
        
        for tag in tags:
            if tag in tagsList:
                tag_id = tagsList[tag]
            else:
                print(f"Tag '{tag}' not found in DB.")
                continue
            insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id)
    
    cursor.commit()
    return

if __name__ == "__main__":
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    
    
    
    conn.close()