from mv_back.db.bookmarks_db import *

# --------------------------------------------------------------
# GETs
def get_skipset_by_id(cursor, skipset_id):
    skipset = select_SkipSet_by_id(cursor, skipset_id)
    if not skipset:
        return {"error": "SkipSet not found", 'status_code': 404, 'id': skipset_id}
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
    return {"data": data, 'status_code': 200}

def get_skpsets_by_episode_id(cursor, episode_id):
    skipsets = select_SkipSets_by_episode_id(cursor, episode_id)
    if not skipsets:
        return {"error": "No SkipSets found for the given episode_id", 'status_code': 404, 'episode_id': episode_id}
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
    return {"data": all_data, 'status_code': 200}

def get_skipset_by_episode_id_and_name(cursor, episode_id, name):
    skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
    if not skipset:
        return {"error": "SkipSet not found for the given episode_id and name", 'status_code': 404, 'episode_id': episode_id, 'name': name}
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
    return {"data": data, 'status_code': 200}

def get_skipranges_by_skipset_id(cursor, skipset_id):
    skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
    if not skipranges:
        return {"error": "No SkipRanges found for the given skipset_id", 'status_code': 404, 'skipset_id': skipset_id}
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
    return {"data": all_data, 'status_code': 200}

def get_skipranges_by_episode_id_and_name(cursor, episode_id, name):
    skipset = select_SkipSet_by_episode_id_and_name(cursor, episode_id, name)
    if not skipset:
        return {"error": "SkipSet not found for the given episode_id and name", 'status_code': 404, 'episode_id': episode_id, 'name': name}
    skipset_id = skipset[0]
    skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
    if not skipranges:
        return {"error": "No SkipRanges found for the given episode_id and name", 'status_code': 404, 'episode_id': episode_id, 'name': name}
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
    return {"data": all_data, 'status_code': 200}


# --------------------------------------------------------------
# POSTs

def create_skipset(cursor, episode_id, source, name='Default', priority=0, is_active=1):
    skipset_id = insert_SkipSet_to_db(cursor, episode_id, source, name, priority, is_active)
    if not skipset_id:
        return {"error": "SkipSet already exists for the given episode_id and source", 'status_code': 400, 'episode_id': episode_id, 'source': source}
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
    return {"data": data, 'status_code': 201}

def create_skiprange(cursor, skipset_id, start, end, label='NULL'):
    skipset = select_SkipSet_by_id(cursor, skipset_id)
    if not skipset:
        return {"error": "SkipSet not found for the given skipset_id", 'status_code': 404, 'skipset_id': skipset_id}
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
    return {"data": data, 'status_code': 201}


# --------------------------------------------------------------
# UPDATEs

def update_skipset(cursor, skipset_id, new_skipset):
    existing_skipset = select_SkipSet_by_id(cursor, skipset_id)
    if not existing_skipset:
        return {"error": "SkipSet not found", 'status_code': 404, 'id': skipset_id}
    
    rows_updated = update_SkipSet_by_id(cursor, skipset_id, new_skipset)
    if rows_updated == 0:
        return {"error": "No changes made to the SkipSet", 'status_code': 400, 'id': skipset_id}
    
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
    return {"data": data, 'status_code': 200}

def update_skiprange(cursor, skiprange_id, new_skiprange):
    existing_skiprange = select_SkipRange_by_id(cursor, skiprange_id)
    if not existing_skiprange:
        return {"error": "SkipRange not found", 'status_code': 404, 'id': skiprange_id}
    
    rows_updated = update_SkipRange_by_id(cursor, skiprange_id, new_skiprange)
    if rows_updated == 0:
        return {"error": "No changes made to the SkipRange", 'status_code': 400, 'id': skiprange_id}
    
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
    return {"data": data, 'status_code': 200}