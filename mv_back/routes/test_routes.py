from flask import request, Blueprint

from mv_back.db.utils import get_series_structure, get_movie_structure



test = Blueprint("test", __name__, url_prefix="/api/test")

@test.route("/media_structure", methods=["GET"])
def test_media_structure_route():
    media_path = request.args.get("path", "")
    
    return get_series_structure(media_path)