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
            
            return {"data": serie}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_series():
    try:
        with db_connection() as cursor:
            series = select_all_series(cursor)
            return {"data": series}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_series_with_tags():
    try:
        with db_connection() as cursor:
            series = select_all_series_with_tags(cursor)
            return {"data": series}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_seasons_by_serie_id(serie_id):
    try:
        with db_connection() as cursor:
            seasons = select_all_seasons_by_serie_id(cursor, serie_id)
            if not seasons:
                return {"error": "No seasons found for this series", 'serie_id': serie_id}, 404
            
            return {"data": seasons}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_episodes_by_season_id(season_id):
    try:
        with db_connection() as cursor:
            episodes = select_all_episodes_by_season_id(cursor, season_id)
            if not episodes:
                return {"error": "No episodes found for this season", 'season_id': season_id}, 404
            
            return {"data": episodes}, 200
    except Exception as e:
        return {"error": str(e)}, 500