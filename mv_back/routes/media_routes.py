from flask import request, Blueprint
from mv_back.api.media_api import *

media = Blueprint("media", __name__, url_prefix="/api/media")


#--------------------------------------------------------------
# GETs

@media.route(f'/', methods=['GET'])
def get_all_media_with_tags_route():
    tags_list = request.args.get('tags', '')
    tags = tags_list.split(',') if tags_list else None
    filter_mode = request.args.get('filter_mode', 'include')  # 'any' або 'all'
    return get_all_media_with_tags(tags, filter_mode)

# @media.route(f'/<media_id>', methods=['GET'])
# def get_media_data_by_id_route(media_id):
#     return get_media_with_tags_by_id(media_id)

@media.route(f'/<media_id>', methods=['GET'])
def get_media_data_by_id_route(media_id):
    return get_media_by_id(media_id)

#--------------------------------------------------------------
#POSTs

@media.route(f'/media_structure_perview', methods=['POST'])
def get_media_structure_perview_route():
    data = request.get_json(force=True)
    media_path = data.get('path', '')
    return get_media_structure_perview(media_path)

#--------------------------------------------------------------
# UPDATEs

@media.route(f'/<media_id>', methods=['POST'])
def update_media_data_by_id_route(media_id):
    data = request.json
    return update_media(media_id, data)