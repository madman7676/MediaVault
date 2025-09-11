import os
import pyodbc
import jmespath
from tqdm import tqdm

from mv_back.db.tags_db import insert_Xref_Tag2Media_to_db

from .utils import *
from ..config import *
from .media_db import *
from .movies_db import *
from .series_db import *
from .bookmarks_db import *
from ..metadata import load_metadata


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

def insert_movies_to_db(cursor):
    paths = os_get_all_items_paths(MOVIES_PATHS)
    for path in tqdm(paths, desc="Inserting movies to DB"):
        insert_movie_collection_to_db(cursor, path)
    return

def insert_series_to_db(cursor):
    paths = os_get_all_items_paths(SERIES_PATHS)
    for path in tqdm(paths, desc="Inserting series to DB"):
        insert_serie_to_db(cursor, path)
    return

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