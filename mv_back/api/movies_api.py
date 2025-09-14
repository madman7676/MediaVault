from mv_back.db.movies_db import *


#--------------------------------------------------------------
# GETs

def get_all_movies_collections(cursor):
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
    return {"data": formatted_collections, 'status_code': 200}

def get_movie_items_by_collection_id(cursor, movie_id):
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
    return {"data": formatted_items, 'status_code': 200}

def get_movie_item_by_id(cursor, item_id):
    item = select_movie_item_by_id(cursor, item_id)
    if not item:
        return {"error": "Movie item not found", 'status_code': 404, 'id': item_id}
    data = {
        'id': item[0],
        'primary_collection_id': item[1],
        'position': item[2],
        'title': item[3],
        'path': item[4]
    }
    return {"data": data, 'status_code': 200}


#--------------------------------------------------------------
# UPDATEs

def update_movie_item_by_id(cursor, item_id, new_item):
    existing_item = select_movie_item_by_id(cursor, item_id)
    if not existing_item:
        return {"error": "Movie item not found", 'status_code': 404, 'id': item_id}
    
    rows_updated = update_movie_item_by_id(cursor, item_id, new_item)
    if rows_updated == 0:
        return {"error": "No changes made to the movie item", 'status_code': 400, 'id': item_id}
    
    updated_item = select_movie_item_by_id(cursor, item_id)
    data = {
        'id': updated_item[0],
        'primary_collection_id': updated_item[1],
        'position': updated_item[2],
        'title': updated_item[3],
        'path': updated_item[4]
    }
    return {"data": data, 'status_code': 200}

def update_movie_collection_by_id(cursor, movie_id, new_data):
    existing_collection = select_all_movies_collections(cursor)
    if not any(col[0] == movie_id for col in existing_collection):
        return {"error": "Movie collection not found", 'status_code': 404, 'id': movie_id}
    
    rows_updated = update_movie_collection_by_id(cursor, movie_id, new_data)
    if rows_updated == 0:
        return {"error": "No changes made to the movie collection", 'status_code': 400, 'id': movie_id}
    
    updated_collection = next((col for col in select_all_movies_collections(cursor) if col[0] == movie_id), None)
    if not updated_collection:
        return {"error": "Movie collection not found after update", 'status_code': 404, 'id': movie_id}
    
    data = {
        'id': updated_collection[0],
        'title': updated_collection[1],
        'path': updated_collection[2],
        'auto_added': updated_collection[3],
        'crD': updated_collection[4],
        'modD': updated_collection[5],
        'delD': updated_collection[6]
    }
    return {"data": data, 'status_code': 200}