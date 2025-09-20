from mv_back.db.utils import db_connection
from mv_back.db.bookmarks_db import *

# --------------------------------------------------------------
# GETs

def get_skipset_by_id(skipset_id):
    try:
        with db_connection() as cursor:
            skipset = select_SkipSet_by_id(cursor, skipset_id)
            if not skipset:
                return {"error": "SkipSet not found", 'id': skipset_id}, 404
            
            skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
            ranges = []
            for sr in skipranges:
                ranges.append({
                    'id': sr[0],
                    'primary_skipset_id': sr[1],
                    'start_time_ms': sr[2],
                    'end_time_ms': sr[3],
                    'label': sr[4],
                    'crD': sr[5],
                    'modD': sr[6],
                    'delD': sr[7]
                })
            
            data = {
                'id': skipset[0],
                'primary_episode_id': skipset[1],
                'name': skipset[2],
                'source': skipset[3],
                'priority': skipset[4],
                'is_active': skipset[5],
                'created_at': skipset[6],
                'modified_at': skipset[7],
                'deleted_at': skipset[8],
                'skip_ranges': ranges
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipsets_by_episode_id(episode_id):
    try:
        with db_connection() as cursor:
            skipsets = select_SkipSets_by_episode_id(cursor, episode_id)
            if not skipsets:
                return {"error": "No SkipSets found for the given episode_id", 'episode_id': episode_id}, 404
            
            all_data = []
            for skipset in skipsets:
                data = {
                    'id': skipset[0],
                    'primary_episode_id': skipset[1],
                    'name': skipset[2],
                    'source': skipset[3],
                    'priority': skipset[4],
                    'is_active': skipset[5],
                    'created_at': skipset[6],
                    'modified_at': skipset[7],
                    'deleted_at': skipset[8]
                }
                all_data.append(data)
            return {"data": all_data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipset_by_episode_id_and_name(episode_id, name):
    try:
        with db_connection() as cursor:
            skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
            if not skipset:
                return {"error": "SkipSet not found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            data = {
                'id': skipset[0],
                'primary_episode_id': skipset[1],
                'name': skipset[2],
                'source': skipset[3],
                'priority': skipset[4],
                'is_active': skipset[5],
                'created_at': skipset[6],
                'modified_at': skipset[7],
                'deleted_at': skipset[8]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipranges_by_skipset_id(skipset_id):
    try:
        with db_connection() as cursor:
            skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
            if not skipranges:
                return {"error": "No SkipRanges found for the given skipset_id", 'skipset_id': skipset_id}, 404
            
            all_data = []
            for sr in skipranges:
                data = {
                    'id': sr[0],
                    'primary_skipset_id': sr[1],
                    'start_time_ms': sr[2],
                    'end_time_ms': sr[3],
                    'label': sr[4],
                    'crD': sr[5],
                    'modD': sr[6],
                    'delD': sr[7]
                }
                all_data.append(data)
            return {"data": all_data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_skipranges_by_episode_id_and_name(episode_id, name):
    try:
        with db_connection() as cursor:
            skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
            if not skipset:
                return {"error": "SkipSet not found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            skipset_id = skipset[0]
            skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
            if not skipranges:
                return {"error": "No SkipRanges found for the given episode_id and name", 'episode_id': episode_id, 'name': name}, 404
            
            all_data = []
            for sr in skipranges:
                data = {
                    'id': sr[0],
                    'primary_skipset_id': sr[1],
                    'start_time_ms': sr[2],
                    'end_time_ms': sr[3],
                    'label': sr[4],
                    'crD': sr[5],
                    'modD': sr[6],
                    'delD': sr[7]
                }
                all_data.append(data)
            return {"data": all_data}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def get_all_default_skipranges_by_episode_id(episode_id):
    try:
        with db_connection() as cursor:
            skipranges = select_all_default_SkipRanges_by_episode_id(cursor, episode_id)
            if not skipranges:
                return {"error": "No default SkipRanges found for the given episode_id", 'episode_id': episode_id}, 404
            
            all_data = []
            for sr in skipranges:
                data = {
                    'id': sr[0],
                    'primary_skipset_id': sr[1],
                    'start_time_ms': sr[2],
                    'end_time_ms': sr[3],
                    'label': sr[4],
                    'crD': sr[5],
                    'modD': sr[6],
                    'delD': sr[7],
                    'primary_media_id': sr[8]
                }
                all_data.append(data)
            return {"data": all_data}, 200
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
            
            skipset = select_SkipSet_by_id(cursor, skipset_id)
            data = {
                'id': skipset[0],
                'primary_episode_id': skipset[1],
                'name': skipset[2],
                'source': skipset[3],
                'priority': skipset[4],
                'is_active': skipset[5],
                'created_at': skipset[6],
                'modified_at': skipset[7],
                'deleted_at': skipset[8]
            }
            return {"data": data}, 201
    except Exception as e:
        return {"error": str(e)}, 500

def create_skiprange(skipset_id, start, end, label='NULL'):
    try:
        with db_connection(commit=True) as cursor:
            skipset = select_SkipSet_by_id(cursor, skipset_id)
            if not skipset:
                return {"error": "SkipSet not found for the given skipset_id", 'skipset_id': skipset_id}, 404
            
            skiprange_id = insert_SkipRange_to_db(cursor, skipset_id, start, end, label)
            skiprange = select_SkipRange_by_id(cursor, skiprange_id)
            
            data = {
                'id': skiprange[0],
                'primary_skipset_id': skiprange[1],
                'start_time_ms': skiprange[2],
                'end_time_ms': skiprange[3],
                'label': skiprange[4],
                'crD': skiprange[5],
                'modD': skiprange[6],
                'delD': skiprange[7]
            }
            return {"data": data}, 201
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
            data = {
                'id': updated_skipset[0],
                'primary_episode_id': updated_skipset[1],
                'name': updated_skipset[2],
                'source': updated_skipset[3],
                'priority': updated_skipset[4],
                'is_active': updated_skipset[5],
                'created_at': updated_skipset[6],
                'modified_at': updated_skipset[7],
                'deleted_at': updated_skipset[8]
            }
            return {"data": data}, 200
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
            data = {
                'id': updated_skiprange[0],
                'primary_skipset_id': updated_skiprange[1],
                'start_time_ms': updated_skiprange[2],
                'end_time_ms': updated_skiprange[3],
                'label': updated_skiprange[4],
                'crD': updated_skiprange[5],
                'modD': updated_skiprange[6],
                'delD': updated_skiprange[7]
            }
            return {"data": data}, 200
    except Exception as e:
        return {"error": str(e)}, 500