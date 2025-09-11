import os
from mv_back.db.utils import *
from datetime import datetime

# --------------------------------------------------------------
# Inserts

def insert_to_Media_table(cursor, path):
    title = os.path.basename(path)
    id = formate_id(cursor, title, "Media")
    query = '''
        INSERT INTO Media (id, title, path, crD) VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (id, title, path, datetime.now()))
    return id


# --------------------------------------------------------------
# Selects

def select_media_by_id(cursor, media_id):
    cursor.execute('SELECT * FROM Media WHERE id = ?', (media_id,))
    result = cursor.fetchone()
    if result:
        return result
    else:
        return None

def select_all_media(cursor):
    cursor.execute('SELECT * FROM Media')
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []

def select_all_media_with_tags(cursor):
    query = '''
        SELECT m.id, m.title, m.[path], m.auto_added, m.crD, m.modD, m.delD,
            JSON_QUERY((
                SELECT tag.[name] AS [value]
                FROM Xref_Tag2Media ref
                left join Tag on tag.id = ref.tag_id
                WHERE ref.media_id = m.id
                FOR JSON PATH
            )) AS tags_json
        FROM Media m;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    if results:
        return results
    else:
        return []


# --------------------------------------------------------------
# Updates

def update_media_by_id(cursor, media_id, new_media):
    query = '''
        UPDATE Media
        SET title = ?, path = ?, modD = ?
        WHERE id = ?;
    '''
    cursor.execute(query, (new_media['title'], new_media['path'], datetime.now(), media_id))
    return cursor.rowcount