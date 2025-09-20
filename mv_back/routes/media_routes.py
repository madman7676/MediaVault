from flask import request, Blueprint
from mv_back.api.media_api import *

media = Blueprint("media", __name__, url_prefix="/api/media")


#--------------------------------------------------------------
# GETs

@media.route(f'/all', methods=['GET'])
def get_all_media_with_tags_route():
    return get_all_media_with_tags()

@media.route(f'/<media_id>', methods=['GET'])
def get_media_data_by_id_route(media_id):
    return get_media_with_tags_by_id(media_id)


#--------------------------------------------------------------
#POSTs



#--------------------------------------------------------------
# UPDATEs

@media.route(f'/<media_id>', methods=['POST'])
def update_media_data_by_id_route(media_id):
    data = request.json
    return update_media(media_id, data)