from datetime import datetime
from config import *
import os
import uuid

from metadata import create_movie_metadata, create_series_metadata

def delete_metadata(conn, media_id):
    """
    Видаляє метадані з бази даних за ID медіа.
    Параметри:
        conn: Підключення до бази даних.
        media_id: ID медіа, яке потрібно видалити.
    Повертає:
        Tuple з результатом операції (True/False, статус код).
    """
    try:
        with conn.cursor() as cursor:
            # Видаляємо з Media
            cursor.execute("UPDATE Media SET deleted = 1 WHERE id = ?", (media_id,))
            if cursor.rowcount == 0:
                return False, 404

            # Видаляємо MediaUnit
            cursor.execute("UPDATE MediaUnit SET deleted = 1 WHERE media_id = ?", (media_id,))

            conn.commit()
            return True, 200
        
    except Exception as e:
        print(f"Error deleting metadata with ID {media_id}: {e}")
        return str(e), 500

def load_media(conn):
    """
    Завантажує всі медіа з бази даних.
    Параметри:
        conn: Підключення до бази даних.
    Повертає:
        Список медіа з бази даних.
    """
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    m.id,
                    m.title,
                    m.path,
                    m.type,
                    m.auto_added,
                    m.last_modified,
                    COUNT(mu.id) AS units_count
                FROM Media m
                LEFT JOIN MediaUnit mu ON mu.media_id = m.id AND mu.deleted = 0
                WHERE m.deleted = 0
                GROUP BY 
                    m.id,
                    m.title,
                    m.path,
                    m.type,
                    m.auto_added,
                    m.last_modified
                ORDER BY m.title

            """
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            media_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return True, media_list, 200

    except Exception as e:
        print(f"Error loading media: {e}")
        return str(e), [], 500

def auto_add_metadata(conn):
    """
    Автоматично додає метадані до бази даних.
    Параметри:
        conn: Підключення до бази даних.
        force_update: Якщо True, оновлює існуючі медіа.
    Повертає:
        Tuple з результатом операції (True/False, статус код).
    """
    try:
        with conn:
            with conn.cursor() as cursor:
                # серіали
                for root_path in SERIES_PATHS:
                    for root, dirs, _ in os.walk(root_path):
                        for d in dirs:
                            dir_path = os.path.join(root, d)
                            if get_media_by_path(cursor, dir_path):
                                continue
                            add_series(cursor, d, dir_path)
                        break                  # тільки верхній рівень

                # фільми
                for root_path in MOVIES_PATHS:
                    for root, dirs, files in os.walk(root_path):
                        # одиничні файли — як колекція з однією частиною
                        for f in files:
                            fp = os.path.join(root, f)
                            if get_media_by_path(cursor, fp):
                                continue
                            add_movie_collection(cursor, f, fp)
                        for d in dirs:
                            dp = os.path.join(root, d)
                            if get_media_by_path(cursor, dp):
                                continue
                            add_movie_collection(cursor, d, dp)
                        break
            return True, 200

    except Exception as e:
        print(f"Error auto-adding metadata: {e}")
        return str(e), 500

def add_media(cursor, media, mtype):
    cursor.execute("""
        INSERT INTO Media (id, title, path, auto_added, last_modified, type)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?)
    """, media["id"], media["title"], media["path"],
         True, datetime.now(), mtype)
    return cursor.fetchone()[0]

def add_media_unit(cursor, media_id, title, path, unit_type, has_episodes):
    cursor.execute("""
        INSERT INTO MediaUnit (media_id, title, path, unit_type, has_episodes)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?)
    """, media_id, title, path, unit_type, has_episodes)
    return cursor.fetchone()[0]

def add_episode(cursor, media_unit_id, name):
    cursor.execute("""
        INSERT INTO Episode (media_unit_id, name)
        OUTPUT INSERTED.id
        VALUES (?, ?)
    """, media_unit_id, name)
    return cursor.fetchone()[0]

def add_series(cursor, directory, path):
    series = create_series_metadata(directory, path)
    sid = add_media(cursor, series, "series")
    for season in series["seasons"]:
        uid = add_media_unit(cursor, sid,
                             season["title"], season["path"],
                             "season", True)
        for ep in season["files"]:
            add_episode(cursor, uid, ep["name"])
    return sid

def add_movie_collection(cursor, directory, path):
    movie = create_movie_metadata(directory, path)
    mid = add_media(cursor, movie, "collection")
    for part in movie["parts"]:
        add_media_unit(cursor, mid,
                       part["title"], part["path"],
                       "part", False)
    return mid
          
def get_media_by_path(cursor, path):
    '''
    Отримує медіа за шляхом.
    Параметри:
        cursor: Курсор для виконання SQL запитів.
        path: Шлях до медіа.
    Повертає:
        ID медіа або None, якщо не знайдено.
    '''
    query = '''
        SELECT id FROM Media WHERE path = ? AND deleted = 0
    '''
    cursor.execute(query, (path,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def get_media_by_id(media_id, conn):
    '''
    Отримує медіа за ID.
    Параметри:
        media_id: ID медіа.
        conn: Підключення до бази даних.
    Повертає:
        Словник з інформацією про медіа або None, якщо не знайдено.
    '''
    with conn.cursor() as cursor:
        query = '''
            SELECT id, title, path, type, auto_added, last_modified
            FROM Media WHERE id = ? AND deleted = 0
        '''
        cursor.execute(query, (media_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    return None

def get_counts(conn):
    '''
    Отримує кількість сезонів/частин у медіа.
    Параметри:
        conn: Підключення до бази даних.
    Повертає:
        Tuple з кількістю сезонів, частин та епізодів.
    '''

def get_media_units_by_media_id(media_id, conn):
    '''
    Отримує медіа-одиниці за ID медіа.
    Параметри:
        media_id: ID медіа.
        conn: Підключення до бази даних.
    Повертає:
        Список медіа-одиниць або None, якщо не знайдено.
    '''
    with conn.cursor() as cursor:
        query = '''
            SELECT * FROM MediaUnit WHERE media_id = ? AND deleted = 0
        '''
        cursor.execute(query, (media_id,))
        media_units = cursor.fetchone()
        if media_units:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in media_units]
    return None

def update_paths(conn, media_id):
    """
    Оновлює шляхи медіа в базі даних.
    Параметри:
        conn: Підключення до бази даних.
        media_id: ID медіа, для якого потрібно оновити шляхи.
    Повертає:
        Tuple з результатом операції (True/False, статус код).
    """
    try:
        with conn.cursor() as cursor:
            # Отримуємо медіа за ID
            media = get_media_by_id(media_id, conn)
            if not media:
                return False, 404

            base_path = media["path"]
            if not os.path.exists(base_path):
                return "Path doesn't exist", 404
            directory=os.path.basename(media["path"])
            
            if media["type"] == "series":
                new_structure = create_series_metadata(directory, base_path)
                
                media_units = get_media_units_by_media_id(media_id, conn)
                if (len(media_units) == 1 and 
                    media_units[0]["title"] == 'Season 1' and 
                    len(new_structure["seasons"]) > 1):
                    query = """
                        UPDATE MediaUnit
                        SET title = ?, path = ?
                        WHERE media_id = ?
                    """
                    cursor.execute(query, new_structure["seasons"][0]["title"], new_structure["seasons"][0]["path"],
                                    "season", True, media_id)
                    cursor.execute('UPDATE Media SET last_modified = ? WHERE id = ?',
                                   datetime.now(), media_id)
                    
                    for season in new_structure["seasons"][1:]:
                        uid = add_media_unit(cursor, media_id,
                                             season["title"], season["path"],
                                             "season", True)
                        for ep in season["files"]:
                            add_episode(cursor, uid, ep["name"])
                        
            elif media["type"] == "collection":
                new_structure = create_movie_metadata(directory, base_path)
            
            conn.commit()
            return True, 200

    except Exception as e:
        print(f"Error updating paths for media ID {media_id}: {e}")
        return str(e), 500