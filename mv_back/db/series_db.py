import os
import json
from natsort import natsorted

from mv_back.db.utils import *
from mv_back.db.media_db import *


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
    tags = []
    if serie[7]:
        tags = [tag['value'] for tag in json.loads(serie[7])]
    
    return {
        'id': serie[0],
        'title': serie[1],
        'tags': tags,
        'count': serie[8],
        'type': serie[9],
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

def select_all_series_with_tags(cursor, tags=None, filter_mode='include'):
    """Повертає всі series з тегами, з можливістю фільтрації за тегами"""
    
    tags_condition = build_tag_filter(tags, filter_mode)
    
    query = f'''
        SELECT m.id, m.title, m.[path], m.auto_added, m.crD, m.modD, m.delD,
            JSON_QUERY((
                SELECT tag.[name] AS [value]
                FROM Xref_Tag2Media ref
                left join Tag on tag.id = ref.tag_id AND tag.delD IS NULL
                WHERE ref.media_id = m.id AND ref.delD IS NULL
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
        INNER JOIN Series s on s.media_id = m.id AND s.delD IS NULL
        WHERE m.delD IS NULL {tags_condition['query']}
        ORDER BY m.title;
    '''
    cursor.execute(query, tags_condition['params'])
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

def select_all_seasons_and_episodes_by_serie_id(cursor, series_id):
    seasons_query = '''
        SELECT id, primary_series_id, season_number, title, path, crD, modD, delD
        FROM Season
        WHERE primary_series_id = ? AND delD IS NULL
        ORDER BY season_number;
    '''
    cursor.execute(seasons_query, (series_id,))
    seasons_results = cursor.fetchall()
    
    if not seasons_results:
        return []
    
    seasons = [format_season(row) for row in seasons_results ]
    
    query = '''
        SELECT e.id, e.primary_season_id, e.episode_number, e.title, e.file_path, e.crD, e.delD, e.modD
        FROM Episode e
        INNER JOIN Season s on e.primary_season_id = s.id
        WHERE s.primary_series_id = ? AND e.delD IS NULL
        ORDER BY s.season_number, e.episode_number;
    '''
    cursor.execute(query, (series_id,))
    
    episodes_results = cursor.fetchall()
    
    episodes = [format_episode(row) for row in episodes_results] if episodes_results else []
    
    seasons_map = {season['id']: season for season in seasons}
    
    # Додаємо порожній список епізодів до всіх сезонів
    for season in seasons_map.values():
        if 'files' not in season: # Обережна ініціалізація
            season['files'] = []
    
    for episode in episodes:
        season_id = episode.get('season_id')
        if season_id in seasons_map:
            seasons_map[season_id]['files'].append(episode)
    
    return seasons