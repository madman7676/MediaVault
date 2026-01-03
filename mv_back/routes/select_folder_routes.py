from flask import request, Blueprint, jsonify
from mv_back.api.select_folder_api import *

select_folder = Blueprint("select_folder", __name__, url_prefix="/api/select_folder")

#--------------------------------------------------------------
# GETs

@select_folder.route(f'/', methods=['GET'])
def get_select_folder_route():
    return get_select_folder()