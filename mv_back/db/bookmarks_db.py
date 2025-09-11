import uuid
from datetime import datetime
from .utils import *


def insert_SkipSet_to_db(cursor, episode_id, source, name='Default', priority=0, is_active=1):
    cursor.execute('SELECT id FROM SkipSet WHERE episode_id = ? AND source = ?', (episode_id, source))
    if cursor.fetchone() is not None:
        print(f"SkipSet for episode_id '{episode_id}' with source '{source}' already exists in DB. Skipping...")
        return None
    
    skipSet_id = formate_id(cursor, name+'-'+episode_id+'-'+source, "SkipSet")    
    query = '''
        INSERT INTO SkipSet (id, episode_id, name, source, priority, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipSet_id, episode_id, name, source, priority, is_active, datetime.now()))
    return skipSet_id

def insert_SkipRange_to_db(cursor, skipset_id, start, end, label='NULL'):
    skipRange_id = str(uuid.uuid4())
    query = '''
        INSERT INTO SkipRange (id, skipset_id, start_time_ms, end_time_ms, label) VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (skipRange_id, skipset_id, start, end, label))
    return skipRange_id