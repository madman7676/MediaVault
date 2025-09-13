import pyodbc
from flask import g, request, Blueprint

from mv_back.api.bookmarks_api import *
from mv_back.config import DB_CONNECTION_STRING

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

# --------------------------------------------------------------
# GETs

@bookmarks.route(f'/skipset/<skipset_id>', methods=['GET'])
def get_skipset_by_id_route(skipset_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_skipset_by_id(cursor, skipset_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@bookmarks.route(f'/skipsets/episode/<episode_id>', methods=['GET'])
def get_skpsets_by_episode_id_route(episode_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_skpsets_by_episode_id(cursor, episode_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@bookmarks.route(f'/skipset/episode/<episode_id>/name/<name>', methods=['GET'])
def get_skipset_by_episode_id_and_name_route(episode_id, name):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_skipset_by_episode_id_and_name(cursor, episode_id, name)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@bookmarks.route(f'/skipranges/skipset/<skipset_id>', methods=['GET'])
def get_skipranges_by_skipset_id_route(skipset_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_skipranges_by_skipset_id(cursor, skipset_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

# --------------------------------------------------------------
# POSTs

@bookmarks.route(f'/skiprange', methods=['POST'])
def insert_skiprange_route():
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        skiprange_id = insert_SkipRange_to_db(
            cursor,
            data['skipset_id'],
            data['start_time_ms'],
            data['end_time_ms'],
            data.get('label', 'NULL')
        )
        cursor.commit()
        response = {"data": {"id": skiprange_id}, 'status_code': 200}
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
        if cursor:
            cursor.rollback()
    finally:
        if cursor:
            cursor.close()
    return response

@bookmarks.route(f'/skipset', methods=['POST'])
def create_skipset_route():
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = create_skipset(
            cursor,
            data['episode_id'],
            data['source'],
            data.get('name', 'Default'),
            data.get('priority', 0),
            data.get('is_active', 1)
        )
        if response.get('status_code') == 201:
            cursor.commit()
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
        if cursor:
            cursor.rollback()
    finally:
        if cursor:
            cursor.close()
    return response

# --------------------------------------------------------------
# UPDATEs

@bookmarks.route(f'/skipset/<skipset_id>', methods=['POST'])
def update_skipset_route(skipset_id):
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = update_skipset(cursor, skipset_id, data)
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

@bookmarks.route(f'/skiprange/<skiprange_id>', methods=['POST'])
def update_skiprange_route(skiprange_id):
    cursor = None
    response = {}
    try:
        data = request.json
        cursor = get_db().cursor()
        response = update_skiprange(cursor, skiprange_id, data)
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