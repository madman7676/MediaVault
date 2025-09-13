import uuid
from datetime import datetime
from .utils import *


# --------------------------------------------------------------
# Inserts

def insert_SkipSet_to_db(cursor, episode_id, source, name='Default', priority=0, is_active=1):
    cursor.execute('SELECT id FROM SkipSet WHERE primary_episode_id = ? AND source = ?', (episode_id, source))
    if cursor.fetchone() is not None:
        print(f"SkipSet for episode_id '{episode_id}' with source '{source}' already exists in DB. Skipping...")
        return None
    
    skipSet_id = formate_id(cursor, name+'-'+episode_id+'-'+source, "SkipSet")    
    query = '''
        INSERT INTO SkipSet (id, primary_episode_id, name, source, priority, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipSet_id, episode_id, name, source, priority, is_active, datetime.now()))
    return skipSet_id

def insert_SkipRange_to_db(cursor, skipset_id, start, end, label='NULL'):
    skipRange_id = str(uuid.uuid4())
    query = '''
        INSERT INTO SkipRange (id, primary_skipset_id, start_time_ms, end_time_ms, label) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipRange_id, skipset_id, start, end, label))
    return skipRange_id

# --------------------------------------------------------------
# Selects

def select_SkipSet_by_id(cursor, skipset_id):
    cursor.execute('SELECT * FROM SkipSet WHERE id = ? AND delD IS NULL', (skipset_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        return None
    
def select_SkipSets_by_episode_id(cursor, episode_id):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_episode_id = ? AND delD IS NULL', (episode_id,))
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []

def select_all_SkipSets_by_media_id(cursor, media_id):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_meida_id = ? AND delD IS NULL', (media_id,))
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []

def select_SkipSet_by_episode_id_and_name(cursor, episode_id, name):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_episode_id = ? AND name = ? AND delD IS NULL', (episode_id, name))
    results = cursor.fetchone()
    if results:
        return results
    else:
        return None
    
def select_SkipRanges_by_skipset_id(cursor, skipset_id):
    cursor.execute('SELECT * FROM SkipRange WHERE primary_skipset_id = ? AND delD IS NULL', (skipset_id,))
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []

def select_SkipRange_by_id(cursor, skiprange_id):
    cursor.execute('SELECT * FROM SkipRange WHERE id = ? AND delD IS NULL', (skiprange_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        return None

# --------------------------------------------------------------
# Updates
def update_SkipSet_by_id(cursor, skipset_id, new_skipset):
    fields = []
    values = []
    for key, value in new_skipset.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(skipset_id)
    set_clause = ", ".join(fields)
    curent_date = datetime.now()
    query = f"UPDATE SkipSet SET {set_clause}, modD = {curent_date} WHERE id = ? AND delD IS NULL"
    cursor.execute(query, tuple(values))
    return cursor.rowcount

def update_SkipRange_by_id(cursor, skiprange_id, new_skiprange):
    fields = []
    values = []
    for key, value in new_skiprange.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(skiprange_id)
    set_clause = ", ".join(fields)
    current_date = datetime.now()
    query = f"UPDATE SkipRange SET {set_clause}, modD = {current_date} WHERE id = ? AND delD IS NULL"
    cursor.execute(query, tuple(values))
    return cursor.rowcount