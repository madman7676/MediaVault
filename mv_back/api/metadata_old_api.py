import json

from mv_back.api.movies_api import get_all_movies_with_tags
from mv_back.api.series_api import *
from mv_back.api.bookmarks_api import *

def get_metadata(cursor):
    categories = {
        "series":[],
        "movies":[],
    }
    
    raw_series = get_all_series_with_tags(cursor)
    
    raw_series = raw_series['data']
    
    query = '''
        SELECT id, primary_series_id, season_number, title, path, crD, modD, delD
        FROM Season
        WHERE delD IS NULL
        ORDER BY season_number
    '''
    cursor.execute(query)
    
    raw_seasons = cursor.fetchall()
    
    query = '''
        SELECT id, primary_season_id, episode_number, title, file_path, crD, modD, delD
        FROM Episode
        WHERE delD IS NULL
        ORDER BY episode_number
    '''
    cursor.execute(query)
    
    raw_episodes = cursor.fetchall()
    
    query = '''
        SELECT sr.id, ss.primary_episode_id, sr.start_time_ms, sr.end_time_ms, sr.crD, sr.modD, sr.delD, sr.primary_media_id
        FROM SkipRange as sr 
        INNER JOIN SkipSet as ss on ss.id = sr.primary_skipset_id AND ss.delD IS NULL
        WHERE ss.name = 'Default' AND sr.delD IS NULL AND ss.delD IS NULL
    '''
    cursor.execute(query)
    
    raw_skipranges = cursor.fetchall()
    
    skipranges = {}
    for skiprange in raw_skipranges:
        key = skiprange[1]
        if key not in skipranges:
            skipranges[key] = []
        skipranges[key].append({
            'start': skiprange[2],
            'end': skiprange[3]
        })
    
    episodes = {}
    for episode in raw_episodes:
        key = episode[1]
        if key not in episodes:
            episodes[key] = []
        episodes[key].append({
            'name': episode[3],
            'timeToSkip': skipranges.get(episode[0], [])
        })
    
    seasons = {}
    for season in raw_seasons:
        key = season[1]
        if key not in seasons:
            seasons[key] = []
        seasons[key].append({
            'title': season[3],
            'path': season[4],
            'files': episodes.get(season[0], [])
        })
    
    series = []
    
    for raw_serie in raw_series:
        series.append({
            'id': raw_serie['id'],
            'title': raw_serie['title'],
            'path': raw_serie['path'],
            'tags': raw_serie['tags'],
            'auto_added': raw_serie['auto_added'],
            'last_modified': raw_serie['modD'] if raw_serie['modD'] else raw_serie['crD'],
            'type': 'series',
            'seasons': seasons.get(raw_serie['id'], [])
        })
    
    categories['series'] = series
    
    raw_movies = get_all_movies_with_tags(cursor)
    
    raw_movies = raw_movies['data']
    
    query = '''
        SELECT id, primary_collection_id, position, title, path
        FROM MovieItem
        WHERE delD IS NULL
        ORDER BY position
    '''
    cursor.execute(query)
    
    raw_movie_items = cursor.fetchall()
    
    movie_items = {}
    for item in raw_movie_items:
        key = item[1]
        if key not in movie_items:
            movie_items[key] = []
        movie_items[key].append({
            'title': item[3],
            'path': item[4]
        })
    
    movies = []
    for raw_movie in raw_movies:
        movies.append({
            'id': raw_movie['id'],
            'title': raw_movie['title'],
            'path': raw_movie['path'],
            'tags': raw_movie['tags'],
            'auto_added': raw_movie['auto_added'],
            'last_modified': raw_movie['modD'] if raw_movie['modD'] else raw_movie['crD'],
            'type': 'collection',
            'parts': movie_items.get(raw_movie['id'], [])
        })
    
    categories['movies'] = movies
    
    return {"data": categories, 'status_code': 200}
