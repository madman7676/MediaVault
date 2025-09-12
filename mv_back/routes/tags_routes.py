import pyodbc
from flask import g, request

from mv_back.config import DB_CONNECTION_STRING
from mv_back.api.tags_api import *

BASE_ROUTE = '/api/tags'

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

def router(tags):
    
    # --------------------------------------------------------------
    # GETs
    
    @tags.route(f'{BASE_ROUTE}/all', methods=['GET'])
    def get_all_tags_route():
        cursor = None
        response = {}
        try:
            cursor = get_db().cursor()
            response = get_tag_list(cursor)
        except Exception as e:
            response = {"error": str(e), 'status_code': 500}
        finally:
            if cursor:
                cursor.close()
        return response
    
    @tags.route(f'{BASE_ROUTE}/media/<media_id>', methods=['GET'])
    def get_tags_by_media_id_route(media_id):
        cursor = None
        response = {}
        try:
            cursor = get_db().cursor()
            response = get_tags_by_media_id(cursor, media_id)
        except Exception as e:
            response = {"error": str(e), 'status_code': 500, 'id': media_id}
        finally:
            if cursor:
                cursor.close()
        return response
    
    
    # --------------------------------------------------------------
    # POSTs
    
    @tags.route(f'{BASE_ROUTE}/add', methods=['POST'])
    def add_tag_to_list_route():
        cursor = None
        response = {}
        try:
            data = request.get_json()
            tag_value = data.get('tag')
            if not tag_value:
                return {"error": "Tag value is required", 'status_code': 400}
            
            cursor = get_db().cursor()
            response = add_tag_to_list(cursor, tag_value)
            if response.get('status_code') == 200:
                cursor.commit()
        except Exception as e:
            response = {"error": str(e), 'status_code': 500, 'tag': tag_value}
            if cursor:
                cursor.rollback()
        finally:
            if cursor:
                cursor.close()
        return response
    
    @tags.route(f'{BASE_ROUTE}/add/<media_id>', methods=['POST'])
    def add_tag_to_media_route(media_id):
        cursor = None
        response = {}
        try:
            data = request.get_json()
            tag_id = data.get('tag_id')
            if not tag_id:
                return {"error": "Tag ID is required", 'status_code': 400, 'media_id': media_id}
            
            cursor = get_db().cursor()
            response = add_tag_to_media(cursor, media_id, tag_id)
            if response.get('status_code') == 200:
                cursor.commit()
        except Exception as e:
            response = {"error": str(e), 'status_code': 500, 'media_id': media_id, 'tag': tag_id}
            if cursor:
                cursor.rollback()
        finally:
            if cursor:
                cursor.close()
        return response
    
    @tags.route(f'{BASE_ROUTE}/remove/<media_id>', methods=['POST'])
    def remove_tag_from_media_route(media_id):
        cursor = None
        response = {}
        try:
            data = request.get_json()
            tag_id = data.get('tag_id')
            if not tag_id:
                return {"error": "Tag ID is required", 'status_code': 400, 'media_id': media_id}
            
            cursor = get_db().cursor()
            response = remove_tag_from_media(cursor, media_id, tag_id)
            if response.get('status_code') == 200:
                cursor.commit()
        except Exception as e:
            response = {"error": str(e), 'status_code': 500, 'media_id': media_id, 'tag_id': tag_id}
            if cursor:
                cursor.rollback()
        finally:
            if cursor:
                cursor.close()
        return response