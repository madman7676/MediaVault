from .utils import formate_id


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
    
    query = '''
        UPDATE Media SET primary_tag_id = ? WHERE id = ?;
    '''
    cursor.execute(query, (tag_id, media_id))
    return True

def select_tags_by_media_id(cursor, media_id):
    query = '''
        SELECT tag.[name]
        FROM Media as md
        INNER JOIN Xref_Tag2Media as t2m on t2m.media_id = md.id
        INNER JOIN Tag on tag.id = t2m.tag_id
        WHERE md.id = ?;
    '''
    cursor.execute(query, (media_id,))
    tags = [row[0] for row in cursor.fetchall()]
    return tags