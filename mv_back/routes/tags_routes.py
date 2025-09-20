from flask import g, request, Blueprint

from mv_back.api.tags_api import *

tags = Blueprint("tags", __name__, url_prefix="/api/tags")

   
# --------------------------------------------------------------
# GETs

@tags.route(f'/all', methods=['GET'])
def get_all_tags_route():
    return get_all_tags_route_handler()

@tags.route(f'/media/<media_id>', methods=['GET'])
def get_tags_by_media_id_route(media_id):
    return get_tags_by_media_id_route_handler(media_id)


# --------------------------------------------------------------
# POSTs

@tags.route(f'/add', methods=['POST'])
def add_tag_to_list_route():
    data = request.get_json()
    return add_tag_to_list_route_handler(data)

@tags.route(f'/add/<media_id>', methods=['POST'])
def add_tag_to_media_route(media_id):
    data = request.get_json()
    return add_tag_to_media_route_handler(media_id, data)

@tags.route(f'/add/bulk', methods=['POST'])
def add_tag_to_list_of_media_route():
    data = request.get_json()
    return add_tag_to_list_of_media_route_handler(data)

@tags.route(f'/remove/<media_id>', methods=['POST'])
def remove_tag_from_media_route(media_id):
    data = request.get_json()
    return remove_tag_from_media_route_handler(media_id, data)