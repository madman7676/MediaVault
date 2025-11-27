import uuid
import pyodbc
from flask import g
from contextlib import contextmanager
from translitua import translit, UkrainianKMU

from mv_back.config import DB_CONNECTION_STRING


def formate_id(cursor, title, table, tries=0):
    base_id = translit(title, table=UkrainianKMU).replace(" ", "_").lower() + ("_(" + str(tries) + ")" if tries > 0 else "")
    cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (base_id,))
    if cursor.fetchone() is None:
        return base_id
    elif tries < 10:
        tries += 1
        return formate_id(cursor, title, table, tries)
    else:
        return base_id[:-4] + str(uuid.uuid4())[:8]
    
def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(DB_CONNECTION_STRING)
    return g.db

def build_tag_filter(tags, mode):
        """mode: 'include' або 'exclude'."""
        
        # 3 і 4 — коли тегів немає
        if not tags:
            if mode == "include":
                return {
                    'query': "",
                    'params': []
                }
            else:  # exclude і тегів немає
                return {
                    'query': """
                        AND m.id NOT IN (
                            SELECT media_id
                            FROM Xref_Tag2Media xt
                            WHERE xt.delD IS NULL
                        )
                    """,
                    'params': []
                }

        # 1 і 2 — коли теги є
        placeholders = ", ".join("?" for _ in tags)

        if mode == "include":
            return {
                'query': f"""
                    AND m.id IN (
                        SELECT xt.media_id
                        FROM Xref_Tag2Media xt
                        JOIN Tag tg ON tg.id = xt.tag_id AND tg.delD IS NULL
                        WHERE xt.delD IS NULL
                        AND tg.[name] IN ({placeholders})
                    )
                """,
                'params': tags
            }

        else:  # mode == exclude
            return {
                'query': f"""
                    AND m.id NOT IN (
                        SELECT xt.media_id
                        FROM Xref_Tag2Media xt
                        JOIN Tag tg ON tg.id = xt.tag_id AND tg.delD IS NULL
                        WHERE xt.delD IS NULL
                        AND tg.[name] IN ({placeholders})
                    )
                """,
                'params': tags
            }

# --------------------------------------------------------------
# Context manager для роботи з БД

@contextmanager
def db_connection(commit=False):
    """
    Context manager для роботи з базою даних
    
    Args:
        commit: True для операцій запису (автоматичний commit/rollback)
    """
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        yield cursor
        
        if commit:
            conn.commit()
            
    except Exception as e:
        if commit and conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()