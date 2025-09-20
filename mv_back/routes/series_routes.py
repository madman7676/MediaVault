from flask import Blueprint
from mv_back.api.series_api import *

series = Blueprint("series", __name__, url_prefix="/api/series")


#--------------------------------------------------------------
# GETs

@series.route("/all", methods=["GET"])
def get_all_series_route():
    return get_all_series()

@series.route("/all_with_tags", methods=["GET"])
def get_all_series_with_tags_route():
    return get_all_series_with_tags()

@series.route("/<media_id>", methods=["GET"])
def get_serie_by_media_id_route(media_id):
    return get_serie_by_media_id(media_id)

@series.route("/<serie_id>/seasons", methods=["GET"])
def get_all_seasons_by_serie_id_route(serie_id):
    return get_all_seasons_by_serie_id(serie_id)

@series.route("/season/<season_id>/episodes", methods=["GET"])
def get_all_episodes_by_season_id_route(season_id):
    return get_all_episodes_by_season_id(season_id)