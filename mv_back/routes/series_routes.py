import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING

series = Blueprint("series", __name__, url_prefix="/api/series")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

def router(series):
    @series.route(f'/all', methods=['GET'])
    def get_all_media_route():
        return {"message": "All media route"}
    