from mv_back.db.utils import db_connection
from mv_back.db.movies_db import *


#--------------------------------------------------------------
# GETs

def get_all_movies_collections():
    try:
        with db_connection() as cursor:
            collections = select_all_movies_collections(cursor)
            return {"data": collections}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_movie_items_by_collection_id(movie_id):
    try:
        with db_connection() as cursor:
            items = select_movie_items_by_collection_id(cursor, movie_id)
            return {"data": items}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_movie_item_by_id(item_id):
    try:
        with db_connection() as cursor:
            item = select_movie_item_by_id(cursor, item_id)
            if not item:
                return {"error": "Movie item not found", 'id': item_id}, 404
            
            return {"data": item}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_movies_with_tags():
    try:
        with db_connection() as cursor:
            all_movies = select_all_movies_with_tags(cursor)
            return {"data": all_movies}, 200
    except Exception as e:
        return {"error": str(e)}, 500

#--------------------------------------------------------------
# UPDATEs

def update_movie_item_by_id(item_id, new_item):
    try:
        with db_connection(commit=True) as cursor:
            existing_item = select_movie_item_by_id(cursor, item_id)
            if not existing_item:
                return {"error": "Movie item not found", 'id': item_id}, 404
            
            rows_updated = update_movie_item_by_id_db(cursor, item_id, new_item)
            if rows_updated == 0:
                return {"error": "No changes made to the movie item", 'id': item_id}, 400
            
            updated_item = select_movie_item_by_id(cursor, item_id)
            return {"data": updated_item}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def update_movie_collection_by_id(movie_id, new_data):
    try:
        with db_connection(commit=True) as cursor:
            # Перевіряємо чи існує колекція
            existing_collection = select_movie_collection_by_id(cursor, movie_id)
            if not existing_collection:
                return {"error": "Movie collection not found", 'id': movie_id}, 404
            
            rows_updated = update_movie_collection_by_id_db(cursor, movie_id, new_data)
            if rows_updated == 0:
                return {"error": "No changes made to the movie collection", 'id': movie_id}, 400
            
            # Отримуємо оновлену колекцію
            updated_collection = select_movie_collection_by_id(cursor, movie_id)
            if not updated_collection:
                return {"error": "Movie collection not found after update", 'id': movie_id}, 404
            
            return {"data": updated_collection}, 200
    except Exception as e:
        return {"error": str(e)}, 500