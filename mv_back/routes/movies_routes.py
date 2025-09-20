from flask import request, Blueprint
from mv_back.api.movies_api import *

movies = Blueprint("movies", __name__, url_prefix="/api/movies")


#--------------------------------------------------------------
# GETs

@movies.route(f'/movies/collections', methods=['GET'])
def get_all_movies_collections_route():
    return get_all_movies_collections()

@movies.route(f'/movies/collection/<movie_id>/items', methods=['GET'])
def get_movie_items_by_collection_id_route(movie_id):
    return get_movie_items_by_collection_id(movie_id)

@movies.route(f'/movies/item/<item_id>', methods=['GET'])
def get_movie_item_by_id_route(item_id):
    return get_movie_item_by_id(item_id)

@movies.route(f'/movies/all', methods=['GET'])
def get_all_movies_with_tags_route():
    return get_all_movies_with_tags()


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