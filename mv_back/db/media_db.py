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
    cursor.execute('SELECT * FROM Media WHERE id = ? AND delD IS NULL', (media_id,))
    result = cursor.fetchone()
    return result or None

def select_all_media(cursor):
    cursor.execute('SELECT * FROM Media WHERE delD IS NULL ORDER BY title;')
    results = cursor.fetchall()
    return results or []

def select_all_media_with_tags(cursor):
    query = '''
        SELECT m.id, m.title, m.[path], m.auto_added, m.crD, m.modD, m.delD,
            JSON_QUERY((
                SELECT tag.[name] AS [value]
                FROM Xref_Tag2Media ref
                left join Tag on tag.id = ref.tag_id AND tag.delD IS NULL
                WHERE ref.media_id = m.id AND ref.delD IS NULL
                FOR JSON PATH
            )) AS tags_json
        FROM Media m
        WHERE m.delD IS NULL
        ORDER BY m.title;
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return results or []


# --------------------------------------------------------------
# Updates

def update_media_by_id(cursor, media_id, new_media):
    fields = []
    values = []
    for key, value in new_media.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(media_id)
    set_clause = ", ".join(fields)
    current_date = datetime.now()
    query = f"UPDATE Media SET {set_clause}, modD = {current_date} WHERE id = ? AND delD IS NULL"
    cursor.execute(query, values)
    return cursor.rowcount