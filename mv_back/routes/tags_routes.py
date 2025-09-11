import pyodbc
from flask import g, request

from mv_back.config import DB_CONNECTION_STRING

BASE_ROUTE = '/api/tags'

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

def router(tags):
    @tags.route(f'{BASE_ROUTE}/all', methods=['GET'])
    def get_all_tags_route():
        return {"message": "All media route"}
    