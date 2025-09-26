import uuid
from datetime import datetime
from .utils import *


# --------------------------------------------------------------
# Formatters (допоміжні функції для форматування)

def format_skipset(skipset):
    """Форматує один skipset record у словник"""
    if not skipset:
        return None
    return {
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

def format_skiprange(skiprange):
    """Форматує один skiprange record у словник"""
    if not skiprange:
        return None
    return {
        'id': skiprange[0],
        'primary_skipset_id': skiprange[1],
        'start_time_ms': skiprange[2],
        'end_time_ms': skiprange[3],
        'label': skiprange[4],
        'crD': skiprange[5],
        'modD': skiprange[6],
        'delD': skiprange[7]
    }

def format_default_skiprange(skiprange):
    """Форматує default skiprange record у словник (з primary_media_id)"""
    if not skiprange:
        return None
    return {
        'id': skiprange[0],
        'primary_skipset_id': skiprange[1],
        'start_time_ms': skiprange[2],
        'end_time_ms': skiprange[3],
        'label': skiprange[4],
        'crD': skiprange[5],
        'modD': skiprange[6],
        'delD': skiprange[7],
        'primary_media_id': skiprange[8]
    }

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
# Selects (тепер повертають відформатовані дані)

def select_SkipSet_by_id(cursor, skipset_id):
    cursor.execute('SELECT * FROM SkipSet WHERE id = ? AND delD IS NULL', (skipset_id,))
    result = cursor.fetchone()
    return format_skipset(result)
    
def select_SkipSets_by_episode_id(cursor, episode_id):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_episode_id = ? AND delD IS NULL', (episode_id,))
    results = cursor.fetchall()
    return [format_skipset(row) for row in results] if results else []

def select_all_SkipSets_by_media_id(cursor, media_id):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_meida_id = ? AND delD IS NULL', (media_id,))
    results = cursor.fetchall()
    return [format_skipset(row) for row in results] if results else []

def select_SkipSet_by_episode_id_and_name(cursor, episode_id, name):
    cursor.execute('SELECT * FROM SkipSet WHERE primary_episode_id = ? AND name = ? AND delD IS NULL', (episode_id, name))
    result = cursor.fetchone()
    return format_skipset(result)
    
def select_SkipRanges_by_skipset_id(cursor, skipset_id):
    cursor.execute('SELECT * FROM SkipRange WHERE primary_skipset_id = ? AND delD IS NULL', (skipset_id,))
    results = cursor.fetchall()
    return [format_skiprange(row) for row in results] if results else []

def select_SkipRange_by_id(cursor, skiprange_id):
    cursor.execute('SELECT * FROM SkipRange WHERE id = ? AND delD IS NULL', (skiprange_id,))
    result = cursor.fetchone()
    return format_skiprange(result)

def select_all_default_SkipRanges_by_episode_id(cursor, episode_id):
    cursor.execute('''
        SELECT sr.id, sr.primary_skipset_id, sr.start_time_ms, sr.end_time_ms, sr.label, sr.crD, sr.modD, sr.delD, sr.primary_media_id
        FROM SkipRange sr
        JOIN SkipSet ss ON sr.primary_skipset_id = ss.id
        WHERE ss.primary_episode_id = ? AND ss.name = 'Default' AND sr.delD IS NULL AND ss.delD IS NULL
    ''', (episode_id,))
    results = cursor.fetchall()
    return [format_default_skiprange(row) for row in results] if results else []

# Нова функція для отримання skipset з ranges
def select_SkipSet_with_ranges_by_id(cursor, skipset_id):
    """Повертає skipset разом з усіма його skipranges"""
    skipset = select_SkipSet_by_id(cursor, skipset_id)
    if not skipset:
        return None
    
    skipranges = select_SkipRanges_by_skipset_id(cursor, skipset_id)
    skipset['skip_ranges'] = skipranges
    return skipset

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