import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING
from mv_back.api.metadata_old_api import get_metadata

metadata = Blueprint("metadata", __name__, url_prefix="/api/metadata")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

@metadata.route(f'/', methods=['GET'])
def get_metadata_route():
    cursor = get_db().cursor()
    return get_metadata(cursor)