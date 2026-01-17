from mv_back.db.utils import db_connection
from mv_back.db.series_db import *


# --------------------------------------------------------------
# GETs

def get_serie_by_media_id(media_id):
    try:
        with db_connection() as cursor:
            serie = select_serie_with_tags_by_id(cursor, media_id)
            if not serie:
                return {"error": "Series not found", 'id': media_id}, 404
            
            return serie, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_series(tags=None, filter_mode='include'):
    try:
        with db_connection() as cursor:
            series = select_all_series(cursor, tags, filter_mode)
            return series, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_series_with_tags(tags=None, filter_mode='include'):
    try:
        with db_connection() as cursor:
            series = select_all_series_with_tags(cursor, tags, filter_mode)
            return series, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_seasons_by_serie_id(serie_id):
    try:
        with db_connection() as cursor:
            seasons = select_all_seasons_by_serie_id(cursor, serie_id)
            if not seasons:
                return {"error": "No seasons found for this series", 'serie_id': serie_id}, 404
            
            return seasons, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_episodes_by_season_id(season_id):
    try:
        with db_connection() as cursor:
            episodes = select_all_episodes_by_season_id(cursor, season_id)
            if not episodes:
                return {"error": "No episodes found for this season", 'season_id': season_id}, 404
            
            return episodes, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
def get_all_seasons_and_episodes_by_serie_id(serie_id):
    try:
        with db_connection() as cursor:
            seasons_and_episodes = select_all_seasons_and_episodes_by_serie_id(cursor, serie_id)
            if not seasons_and_episodes:
                return {"error": "No seasons or episodes found for this series", 'serie_id': serie_id}, 404
            
            return seasons_and_episodes, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
# --------------------------------------------------------------
# POSTs

def add_new_serie(new_serie_path):
    try:
        with db_connection(commit=True) as cursor:
            new_serie = insert_new_serie_to_db(cursor, new_serie_path)

            return {"message": "New series added successfully", "serie": new_serie}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def add_new_season_to_serie(serie_id, new_season_path):
    try:
        with db_connection(commit=True) as cursor:
            new_season = insert_new_season_to_db(cursor, serie_id, new_season_path)
            return {"message": "New season added successfully", "season": new_season}, 201
    except Exception as e:
        return {"error": str(e)}, 500

# --------------------------------------------------------------
# SERVICEs

def manage_add_series(form_data):
    try:
        with db_connection(commit=True) as cursor:
            media_path = form_data.get('selectedFolderPath', '')
            is_new_media = form_data.get('isNewMedia', True)
            if is_new_media:
                res = insert_new_serie_to_db(cursor, media_path)
            else:
                serie_id = form_data.get('selectedMedia', None)
                if not serie_id:
                    return {"error": "selectedMedia is required for existing media"}, 400
                res = insert_new_season_to_db(cursor, serie_id, media_path)
            
            return {"message": "Series management successful", "result": res}, 200
    except Exception as e:
        return {"error": str(e)}, 500