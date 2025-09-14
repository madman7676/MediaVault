import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING
from mv_back.api.movies_api import *

movies = Blueprint("movies", __name__, url_prefix="/api/movies")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db


#--------------------------------------------------------------
# GETs

@movies.route(f'/movies/collections', methods=['GET'])
def get_all_movies_collections_route():
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_all_movies_collections(cursor)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@movies.route(f'/movies/collection/<movie_id>/items', methods=['GET'])
def get_movie_items_by_collection_id_route(movie_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_movie_items_by_collection_id(cursor, movie_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@movies.route(f'/movies/item/<item_id>', methods=['GET'])
def get_movie_item_by_id_route(item_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_movie_item_by_id(cursor, item_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response


#--------------------------------------------------------------
# POSTs




#--------------------------------------------------------------
# UPDATEs

@movies.route(f'/movies/item/<item_id>', methods=['POST'])
def update_movie_item_by_id_route(item_id):
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = update_movie_item_by_id(cursor, item_id, data)
        if response.get('status_code') == 200:
            cursor.commit()
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
        if cursor:
            cursor.rollback()
    finally:
        if cursor:
            cursor.close()
    return response

@movies.route(f'/movies/collection/<movie_id>', methods=['POST'])
def update_movie_collection_by_id_route(movie_id):
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = update_movie_collection_by_id(cursor, movie_id, data)
        if response.get('status_code') == 200:
            cursor.commit()
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
        if cursor:
            cursor.rollback()
    finally:
        if cursor:
            cursor.close()
    return response

