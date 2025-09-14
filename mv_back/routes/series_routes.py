import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING
from mv_back.api.series_api import *

series = Blueprint("series", __name__, url_prefix="/api/series")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db


#--------------------------------------------------------------
# GETs

@series.route("/all", methods=["GET"])
def get_all_series():
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_all_series(cursor)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@series.route("/all_with_tags", methods=["GET"])
def get_all_series_with_tags_route():
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_all_series_with_tags(cursor)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

@series.route("/<media_id>", methods=["GET"])
def get_serie_by_media_id_route(media_id):
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        response = get_serie_by_media_id(cursor, media_id)
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response

