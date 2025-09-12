import json

from mv_back.db.tags_db import *


# --------------------------------------------------------------
# GETs

def get_tags_by_media_id(cursor, media_id):
    tags = select_tags_by_media_id(cursor, media_id)
    if not tags:
        return {"error": "No tags found for this media", 'status_code': 404, 'id': media_id}
    return {"data": tags, 'status_code': 200}

def get_tag_list(cursor):
    tags = select_tag_list(cursor)
    if not tags:
        return {"error": "No tags found", 'status_code': 404}
    return {"data": tags, 'status_code': 200}


# --------------------------------------------------------------
# ADDs

def add_tag_to_list(cursor, tag_value):
    existing_tag = select_tag_by_name(cursor, tag_value)
    if existing_tag:
        return {"error": "Tag already exists", 'status_code': 400, 'tag': tag_value}
    
    rows_inserted = insert_Tag_to_db(cursor, tag_value)
    if rows_inserted == 0:
        return {"error": "Failed to add tag", 'status_code': 500, 'tag': tag_value}
    
    return {"message": "Tag added successfully", 'status_code': 200, 'tag': tag_value}

def add_tag_to_media(cursor, media_id, tag_id):
    
    if not tag_id:
        return {"error": "Failed to add or find tag", 'status_code': 500, 'tag': tag_id}
    
    success = insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id)
    if not success:
        return {"error": "Tag already associated with media", 'status_code': 400, 'media_id': media_id, 'tag': tag_id}
    
    return {"message": "Tag associated with media successfully", 'status_code': 200, 'media_id': media_id, 'tag': tag_id}


# --------------------------------------------------------------
# REMOVEs

def remove_tag_from_media(cursor, media_id, tag_id):
    tag = select_tag_by_id(cursor, tag_id)
    if not tag:
        return {"error": "Tag not found", 'status_code': 404, 'tag_id': tag_id}
    
    success = delete_tag_from_media(cursor, tag_id, media_id)
    if not success:
        return {"error": "Tag not associated with media", 'status_code': 400, 'media_id': media_id, 'tag_id': tag_id}
    
    return {"message": "Tag removed from media successfully", 'status_code': 200, 'media_id': media_id, 'tag_id': tag_id}

def remove_tag_from_db(cursor, tag_id):
    tag = select_tag_by_id(cursor, tag_id)
    if not tag:
        return {"error": "Tag not found", 'status_code': 404, 'tag_id': tag_id}
    
    success = delete_tag_from_db(cursor, tag_id)
    if not success:
        return {"error": "Failed to delete tag", 'status_code': 500, 'tag_id': tag_id}
    
    return {"message": "Tag deleted successfully", 'status_code': 200, 'tag_id': tag_id}