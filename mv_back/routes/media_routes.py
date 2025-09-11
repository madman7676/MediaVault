import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING
from mv_back.api.media_api import *

media = Blueprint("media", __name__, url_prefix="/api/media")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

@media.route(f'/all', methods=['GET'])
def get_all_media_route():
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_all_media_with_tags(cursor)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@media.route(f'/<media_id>', methods=['GET'])
def get_media_data_by_id(media_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_media_by_id(cursor, media_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@media.route(f'/<media_id>', methods=['POST'])
def update_media_data_by_id(media_id):
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = update_media(cursor, media_id, data)
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