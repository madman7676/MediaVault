from flask import request, Blueprint
from mv_back.api.movies_api import *

movies = Blueprint("movies", __name__, url_prefix="/api/movies")


#--------------------------------------------------------------
# GETs

@movies.route(f'/', methods=['GET'])
def get_all_movies_with_tags_route():
    tags_list = request.args.get('tags', '')
    tags = tags_list.split(',') if tags_list else None
    filter_mode = request.args.get('filter_mode', 'include')  # 'any' або 'all'
    return get_all_movies_with_tags(tags, filter_mode)

@movies.route(f'/collections', methods=['GET'])
def get_all_movies_collections_route():
    return get_all_movies_collections()

@movies.route(f'/collection/<movie_id>/movie_items', methods=['GET'])
def get_movie_items_by_collection_id_route(movie_id):
    return get_movie_items_by_collection_id(movie_id)

@movies.route(f'/item/<item_id>', methods=['GET'])
def get_movie_item_by_id_route(item_id):
    return get_movie_item_by_id(item_id)


#--------------------------------------------------------------
# POSTs




#--------------------------------------------------------------
# UPDATEs

@movies.route(f'/movies/item/<item_id>', methods=['POST'])
def update_movie_item_by_id_route(item_id):
    data = request.json
    return update_movie_item_by_id(item_id, data)

@movies.route(f'/movies/collection/<movie_id>', methods=['POST'])
def update_movie_collection_by_id_route(movie_id):
    data = request.json
    return update_movie_collection_by_id(movie_id, data)