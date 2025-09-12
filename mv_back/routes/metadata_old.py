import pyodbc
from flask import g, request, Blueprint

from mv_back.config import DB_CONNECTION_STRING

metadata = Blueprint("metadata", __name__, url_prefix="/api/metadata")

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

@metadata.route(f'/', methods=['GET'])
def get_all_metadata_route():
    cursor = None
    response = {}
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM Metadata")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        response = {"data": data, "status_code": 200}
    except Exception as e:
        response = {"error": str(e), 'status_code': 500}
    finally:
        if cursor:
            cursor.close()
    return response