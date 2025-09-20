from flask import request, Blueprint
from mv_back.api.bookmarks_api import *

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")

# --------------------------------------------------------------
# GETs

@bookmarks.route(f'/skipset/<skipset_id>', methods=['GET'])
def get_skipset_by_id_route(skipset_id):
    return get_skipset_by_id(skipset_id)

@bookmarks.route(f'/skipsets/episode/<episode_id>', methods=['GET'])
def get_skipsets_by_episode_id_route(episode_id):
    return get_skipsets_by_episode_id(episode_id)

@bookmarks.route(f'/skipset/episode/<episode_id>/name/<name>', methods=['GET'])
def get_skipset_by_episode_id_and_name_route(episode_id, name):
    return get_skipset_by_episode_id_and_name(episode_id, name)

@bookmarks.route(f'/skipranges/skipset/<skipset_id>', methods=['GET'])
def get_skipranges_by_skipset_id_route(skipset_id):
    return get_skipranges_by_skipset_id(skipset_id)

@bookmarks.route(f'/skipranges/episode/<episode_id>/name/<name>', methods=['GET'])
def get_skipranges_by_episode_id_and_name_route(episode_id, name):
    return get_skipranges_by_episode_id_and_name(episode_id, name)

@bookmarks.route(f'/skipranges/episode/<episode_id>/default', methods=['GET'])
def get_all_default_skipranges_by_episode_id_route(episode_id):
    return get_all_default_skipranges_by_episode_id(episode_id)

# --------------------------------------------------------------
# POSTs

@bookmarks.route(f'/skiprange', methods=['POST'])
def insert_skiprange_route():
    data = request.json
    return insert_skiprange_direct(
        data['skipset_id'],
        data['start_time_ms'],
        data['end_time_ms'],
        data.get('label', 'NULL')
    )

@bookmarks.route(f'/skipset', methods=['POST'])
def create_skipset_route():
    data = request.json
    return create_skipset(
        data['episode_id'],
        data['source'],
        data.get('name', 'Default'),
        data.get('priority', 0),
        data.get('is_active', 1)
    )

@bookmarks.route(f'/skiprange/full', methods=['POST'])
def create_skiprange_route():
    data = request.json
    return create_skiprange(
        data['skipset_id'],
        data['start_time_ms'],
        data['end_time_ms'],
        data.get('label', 'NULL')
    )

# --------------------------------------------------------------
# UPDATEs

@bookmarks.route(f'/skipset/<skipset_id>', methods=['POST'])
def update_skipset_route(skipset_id):
    data = request.json
    return update_skipset(skipset_id, data)

@bookmarks.route(f'/skiprange/<skiprange_id>', methods=['POST'])
def update_skiprange_route(skiprange_id):
    data = request.json
    return update_skiprange(skiprange_id, data)