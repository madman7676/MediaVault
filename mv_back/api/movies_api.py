import json

from mv_back.db.utils import db_connection
from mv_back.db.movies_db import *
from mv_back.thumbnails import get_or_create_thumbnail


#--------------------------------------------------------------
# GETs

def get_all_movies_collections():
    try:
        with db_connection() as cursor:
            collections = select_all_movies_collections(cursor)
            formatted_collections = []
            for collection in collections:
                formatted_collections.append({
                    'id': collection[0],
                    'title': collection[1],
                    'path': collection[2],
                    'auto_added': collection[3],
                    'crD': collection[4],
                    'modD': collection[5],
                    'delD': collection[6]
                })
            return {"data": formatted_collections}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_movie_items_by_collection_id(movie_id):
    try:
        with db_connection() as cursor:
            items = select_movie_items_by_collection_id(cursor, movie_id)
            formatted_items = []
            for item in items:
                formatted_items.append({
                    'id': item[0],
                    'primary_collection_id': item[1],
                    'position': item[2],
                    'title': item[3],
                    'path': item[4]
                })
            return {"data": formatted_items}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_movie_item_by_id(item_id):
    try:
        with db_connection() as cursor:
            item = select_movie_item_by_id(cursor, item_id)
            if not item:
                return {"error": "Movie item not found", 'id': item_id}, 404
            
            data = {
                'id': item[0],
                'primary_collection_id': item[1],
                'position': item[2],
                'title': item[3],
                'path': item[4]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_movies_with_tags():
    try:
        with db_connection() as cursor:
            all_movies = select_all_movies_with_tags(cursor)
            if not all_movies:
                return {"data": []}, 200
            
            formatted_movies = []
            for movie in all_movies:
                tags = []
                if movie[7]:
                    tags = [tag['value'] for tag in json.loads(movie[7])]
                formatted_movies.append({
                    'id': movie[0],
                    'title': movie[1],
                    'path': movie[2],
                    'tags': tags,
                    'img_path': get_or_create_thumbnail(movie[2]),
                    'auto_added': movie[3],
                    'crD': movie[4],
                    'modD': movie[5],
                    'delD': movie[6]
                })
            return {"data": formatted_movies}, 200
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
            data = {
                'id': updated_item[0],
                'primary_collection_id': updated_item[1],
                'position': updated_item[2],
                'title': updated_item[3],
                'path': updated_item[4]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def update_movie_collection_by_id(movie_id, new_data):
    try:
        with db_connection(commit=True) as cursor:
            # Перевіряємо чи існує колекція
            existing_collection = select_all_movies_collections(cursor)
            if not any(col[0] == movie_id for col in existing_collection):
                return {"error": "Movie collection not found", 'id': movie_id}, 404
            
            rows_updated = update_movie_collection_by_id_db(cursor, movie_id, new_data)
            if rows_updated == 0:
                return {"error": "No changes made to the movie collection", 'id': movie_id}, 400
            
            # Отримуємо оновлену колекцію
            updated_collection = next((col for col in select_all_movies_collections(cursor) if col[0] == movie_id), None)
            if not updated_collection:
                return {"error": "Movie collection not found after update", 'id': movie_id}, 404
            
            data = {
                'id': updated_collection[0],
                'title': updated_collection[1],
                'path': updated_collection[2],
                'auto_added': updated_collection[3],
                'crD': updated_collection[4],
                'modD': updated_collection[5],
                'delD': updated_collection[6]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500