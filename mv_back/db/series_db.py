import os
import json
from natsort import natsorted

from mv_back.db.utils import *
from mv_back.db.media_db import *
from mv_back.thumbnails import get_or_create_thumbnail


# --------------------------------------------------------------
# Formatters (допоміжні функції для форматування)

def format_series(serie):
    """Форматує series record у словник"""
    if not serie:
        return None
    return {
        'id': serie[0],
        'title': serie[1],
        'path': serie[2],
        'auto_added': serie[3],
        'crD': serie[4],
        'modD': serie[5],
        'delD': serie[6]
    }

def format_series_with_thumbnail(serie):
    """Форматує series з thumbnail"""
    if not serie:
        return None
    return {
        'id': serie[0],
        'title': serie[1],
        'img_path': get_or_create_thumbnail(serie[2]),
        'path': serie[2],
        'auto_added': serie[3],
        'crD': serie[4],
        'modD': serie[5],
        'delD': serie[6]
    }

def format_series_with_tags(serie, tags=None):
    """Форматує series з тегами та thumbnail"""
    if not serie:
        return None
    
    # Якщо це результат з select_all_series_with_tags (з JSON тегами)
    if len(serie) == 8 and serie[7] is not None:
        tags = []
        if serie[7]:
            tags = [tag['value'] for tag in json.loads(serie[7])]
    
    return {
        'id': serie[0],
        'title': serie[1],
        'tags': tags if tags is not None else [],
        'img_path': get_or_create_thumbnail(serie[2]),
        'path': serie[2],
        'auto_added': serie[3],
        'crD': serie[4],
        'modD': serie[5],
        'delD': serie[6]
    }

def format_season(season):
    """Форматує season record у словник"""
    if not season:
        return None
    return {
        'id': season[0],
        'serie_id': season[1],
        'season_number': season[2],
        'title': season[3],
        'path': season[4],
        'crD': season[5],
        'modD': season[6],
        'delD': season[7]
    }

def format_episode(episode):
    """Форматує episode record у словник"""
    if not episode:
        return None
    return {
        'id': episode[0],
        'season_id': episode[1],
        'episode_number': episode[2],
        'title': episode[3],
        'file_path': episode[4],
        'crD': episode[5],
        'modD': episode[6],
        'delD': episode[7]
    }


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
        INSERT INTO Episode (id, primary_season_id, episode_number, title, file_path) VALUES (?, ?, ?, ?, ?);
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
# Selects (тепер повертають відформатовані дані)

def select_serie_by_id(cursor, series_id):
    query = '''
        SELECT *
        FROM Media as md
        INNER JOIN Series as sr on sr.media_id = md.id AND sr.delD IS NULL
        WHERE md.id = ? AND md.delD IS NULL;
    '''
    cursor.execute(query, (series_id,))
    result = cursor.fetchone()
    return format_series(result)

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
    return [format_series_with_thumbnail(row) for row in results] if results else []

def select_all_series_with_tags(cursor):
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
        INNER JOIN Series s on s.media_id = m.id AND s.delD IS NULL
        WHERE m.delD IS NULL
        ORDER BY m.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return [format_series_with_tags(row) for row in results] if results else []

# Нова функція для отримання серіалу з тегами за ID
def select_serie_with_tags_by_id(cursor, series_id):
    """Повертає series з тегами за ID"""
    from mv_back.db.tags_db import select_tags_by_media_id
    
    serie = select_serie_by_id(cursor, series_id)
    if not serie:
        return None
    
    tags = select_tags_by_media_id(cursor, series_id)
    return format_series_with_tags([
        serie['id'], serie['title'], serie['path'],
        serie['auto_added'], serie['crD'], serie['modD'], serie['delD']
    ], tags)

def select_all_seasons_by_serie_id(cursor, series_id):
    query = '''
        SELECT id, primary_series_id, season_number, title, path, crD, modD, delD
        FROM Season
        WHERE primary_series_id = ? AND delD IS NULL
        ORDER BY season_number;
    '''
    cursor.execute(query, (series_id,))
    results = cursor.fetchall()
    return [format_season(row) for row in results] if results else []

def select_all_episodes_by_season_id(cursor, season_id):
    query = '''
        SELECT id, primary_season_id, episode_number, title, file_path, crD, modD, delD
        FROM Episode
        WHERE primary_season_id = ? AND delD IS NULL
        ORDER BY episode_number;
    '''
    cursor.execute(query, (season_id,))
    results = cursor.fetchall()
    return [format_episode(row) for row in results] if results else []