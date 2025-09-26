from mv_back.db.utils import db_connection
from mv_back.db.bookmarks_db import *

# --------------------------------------------------------------
# GETs

def get_skipset_by_id(skipset_id):
    try:
        with db_connection() as cursor:
            skipset_data = select_SkipSet_with_ranges_by_id(cursor, skipset_id)
            if not skipset_data:
                return {"error": "SkipSet not found", 'id': skipset_id}, 404
            
            return {"data": skipset_data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipsets_by_episode_id(episode_id):
    try:
        with db_connection() as cursor:
            skipsets = select_SkipSets_by_episode_id(cursor, episode_id)
            if not skipsets:
                return {"error": "No SkipSets found for the given episode_id", 'episode_id': episode_id}, 404
            
            return {"data": skipsets}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipset_by_episode_id_and_name(episode_id, name):
    try:
        with db_connection() as cursor:
            skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
            if not skipset:
                return {"error": "SkipSet not found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            return {"data": skipset}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipranges_by_skipset_id(skipset_id):
    try:
        with db_connection() as cursor:
            skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
            if not skipranges:
                return {"error": "No SkipRanges found for the given skipset_id", 'skipset_id': skipset_id}, 404
            
            return {"data": skipranges}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipranges_by_episode_id_and_name(episode_id, name):
    try:
        with db_connection() as cursor:
            skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
            if not skipset:
                return {"error": "SkipSet not found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            skipset_id = skipset['id']  # Тепер це словник, не tuple
            skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
            if not skipranges:
                return {"error": "No SkipRanges found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            return {"data": skipranges}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_default_skipranges_by_episode_id(episode_id):
    try:
        with db_connection() as cursor:
            skipranges = select_all_default_SkipRanges_by_episode_id(cursor, episode_id)
            if not skipranges:
                return {"error": "No default SkipRanges found for the given episode_id", 'episode_id': episode_id}, 404
            
            return {"data": skipranges}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# --------------------------------------------------------------
# POSTs

def create_skipset(episode_id, source, name='Default', priority=0, is_active=1):
    try:
        with db_connection(commit=True) as cursor:
            skipset_id = insert_SkipSet_to_db(cursor, episode_id, source, name, priority, is_active)
            if not skipset_id:
                return {"error": "SkipSet already exists for the given episode_id and source", 'episode_id': episode_id, 'source': source}, 400
            
            skipset_data = select_SkipSet_by_id(cursor, skipset_id)
            return {"data": skipset_data}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def create_skiprange(skipset_id, start, end, label='NULL'):
    try:
        with db_connection(commit=True) as cursor:
            skipset = select_SkipSet_by_id(cursor, skipset_id)
            if not skipset:
                return {"error": "SkipSet not found for the given skipset_id", 'skipset_id': skipset_id}, 404
            
            skiprange_id = insert_SkipRange_to_db(cursor, skipset_id, start, end, label)
            skiprange_data = select_SkipRange_by_id(cursor, skiprange_id)
            
            return {"data": skiprange_data}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def insert_skiprange_direct(skipset_id, start_time_ms, end_time_ms, label='NULL'):
    """Пряме додавання skiprange (для зворотної сумісності з routes)"""
    try:
        with db_connection(commit=True) as cursor:
            skiprange_id = insert_SkipRange_to_db(cursor, skipset_id, start_time_ms, end_time_ms, label)
            return {"data": {"id": skiprange_id}}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# --------------------------------------------------------------
# UPDATEs

def update_skipset(skipset_id, new_skipset):
    try:
        with db_connection(commit=True) as cursor:
            existing_skipset = select_SkipSet_by_id(cursor, skipset_id)
            if not existing_skipset:
                return {"error": "SkipSet not found", 'id': skipset_id}, 404
            
            rows_updated = update_SkipSet_by_id(cursor, skipset_id, new_skipset)
            if rows_updated == 0:
                return {"error": "No changes made to the SkipSet", 'id': skipset_id}, 400
            
            updated_skipset = select_SkipSet_by_id(cursor, skipset_id)
            return {"data": updated_skipset}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def update_skiprange(skiprange_id, new_skiprange):
    try:
        with db_connection(commit=True) as cursor:
            existing_skiprange = select_SkipRange_by_id(cursor, skiprange_id)
            if not existing_skiprange:
                return {"error": "SkipRange not found", 'id': skiprange_id}, 404
            
            rows_updated = update_SkipRange_by_id(cursor, skiprange_id, new_skiprange)
            if rows_updated == 0:
                return {"error": "No changes made to the SkipRange", 'id': skiprange_id}, 400
            
            updated_skiprange = select_SkipRange_by_id(cursor, skiprange_id)
            return {"data": updated_skiprange}, 200
    except Exception as e:
        return {"error": str(e)}, 500