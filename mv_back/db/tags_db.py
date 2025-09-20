from .utils import formate_id


# --------------------------------------------------------------
# Inserts

def insert_Tag_to_db(cursor, name):
    cursor.execute('SELECT id FROM Tag WHERE name = ?', (name,))
    if cursor.fetchone() is not None:
        print(f"Tag '{name}' already exists in DB. Skipping...")
        return cursor.fetchone()[0]
    
    id = formate_id(cursor, name, "Tag")
    query = '''
        INSERT INTO Tag (id, name) VALUES (?, ?);
    '''
    cursor.execute(query, (id, name))
    return id

def insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id):
    cursor.execute('SELECT * FROM Xref_Tag2Media WHERE media_id = ? AND tag_id = ?', (media_id, tag_id))
    if cursor.fetchone() is not None:
        print(f"Xref_Tag2Media for media_id '{media_id}' and tag_id '{tag_id}' already exists in DB. Skipping...")
        return False
    
    query = '''
        INSERT INTO Xref_Tag2Media (media_id, tag_id) VALUES (?, ?);
    '''
    cursor.execute(query, (media_id, tag_id))
    return True

def insert_Xref_Tag2Media_bulk_to_db(cursor, media_ids, tag_id):
    if not media_ids:
        return 0
    placeholders = ','.join('?' for _ in media_ids)
    query = f'''
        INSERT INTO Xref_Tag2Media (media_id, tag_id)
        SELECT m.id, ?
        FROM Media m
        WHERE m.id IN ({placeholders})
        AND NOT EXISTS (
            SELECT 1 FROM Xref_Tag2Media
            WHERE media_id = m.id AND tag_id = ?
        );
    '''
    cursor.execute(query, (tag_id, *media_ids, tag_id))
    
    updated_rows = cursor.rowcount
    
    if updated_rows == 0:
        print(f"All media_ids already have the tag_id '{tag_id}' associated. No new associations made.")
    return updated_rows
    

# --------------------------------------------------------------
# Selects

def select_tag_list(cursor):
    query = '''
        SELECT name FROM Tag WHERE delD IS NULL ORDER BY name;
    '''
    cursor.execute(query)
    tags = [row[0] for row in cursor.fetchall()]
    return tags

def select_tag_by_id(cursor, tag_id):
    query = '''
        SELECT * FROM Tag WHERE id = ? and delD IS NULL;
    '''
    cursor.execute(query, (tag_id,))
    tag = cursor.fetchone()
    return tag

def select_tags_by_media_id(cursor, media_id):
    query = '''
        SELECT tag.[name]
        FROM Media as md
        INNER JOIN Xref_Tag2Media as t2m on t2m.media_id = md.id AND t2m.delD IS NULL
        INNER JOIN Tag on tag.id = t2m.tag_id AND tag.delD IS NULL
        WHERE md.id = ? AND md.delD IS NULL;
    '''
    cursor.execute(query, (media_id,))
    tags = [row[0] for row in cursor.fetchall()]
    return tags

def select_tag_by_name(cursor, tag_name):
    query = '''
        SELECT * FROM Tag WHERE name = ? and delD IS NULL;
    '''
    cursor.execute(query, (tag_name,))
    tag = cursor.fetchone()
    return tag

# --------------------------------------------------------------
# Deletes

def delete_tag_from_media(cursor, tag_id, media_id):
    query = '''
        UPDATE Xref_Tag2Media
        SET delD = SYSUTCDATETIME()
        WHERE tag_id = ? AND media_id = ? AND delD IS NULL;
    '''
    cursor.execute(query, (tag_id, media_id))
    return cursor.rowcount > 0

def delete_tag_from_db(cursor, tag_id):
    query = '''
        UPDATE Tag
        SET delD = SYSUTCDATETIME()
        WHERE id = ? AND delD IS NULL;
    '''
    cursor.execute(query, (tag_id,))
    return cursor.rowcount > 0