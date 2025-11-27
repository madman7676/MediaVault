from flask import Blueprint, request
from mv_back.api.series_api import *

series = Blueprint("series", __name__, url_prefix="/api/series")


#--------------------------------------------------------------
# GETs

@series.route("/", methods=["GET"])
def get_all_series_with_tags_route():
    tags = request.args.getlist('tags[]')
    filter_mode = request.args.get('filter_mode', 'include')  # 'any' або 'all'
    return get_all_series_with_tags(tags, filter_mode)

@series.route("/<media_id>", methods=["GET"])
def get_serie_by_media_id_route(media_id):
    return get_serie_by_media_id(media_id)

@series.route("/<serie_id>/seasons", methods=["GET"])
def get_all_seasons_by_serie_id_route(serie_id):
    return get_all_seasons_by_serie_id(serie_id)

@series.route("/season/<season_id>/episodes", methods=["GET"])
def get_all_episodes_by_season_id_route(season_id):
    return get_all_episodes_by_season_id(season_id)

@series.route("/<serie_id>/episodes", methods=["GET"])
def get_all_seasons_and_episodes_by_serie_id_route(serie_id):
    return get_all_seasons_and_episodes_by_serie_id(serie_id)