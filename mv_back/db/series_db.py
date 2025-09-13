import os
from natsort import natsorted

from mv_back.db.utils import *
from mv_back.db.media_db import *


# --------------------------------------------------------------
# Inserts

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
        INSERT INTO Season (id, primary_series_id, season_number, title, path) VALUES (?, ?, ?, ?, ?);
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

# --------------------------------------------------------------
# Selects

def select_serie_by_id(cursor, series_id):
    query = '''
        SELECT *
        FROM Media as md
        INNER JOIN Series as sr on sr.media_id = md.id AND sr.delD IS NULL
        WHERE md.id = ? AND md.delD IS NULL;
    '''
    cursor.execute(query, (series_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        return None

def select_all_series(cursor):
    query = '''
        SELECT *
        FROM Media as md
        INNER JOIN Series as sr on sr.media_id = md.id AND sr.delD IS NULL
        WHERE md.delD IS NULL
        ORDER BY md.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return results