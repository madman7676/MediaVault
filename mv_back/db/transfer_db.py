import os
import pyodbc
import jmespath
from tqdm import tqdm

from mv_back.db.tags_db import insert_Xref_Tag2Media_to_db, select_tag_by_name, insert_Tag_to_db

from .utils import *
from ..config import *
from .media_db import *
from .movies_db import *
from .series_db import *
from .bookmarks_db import *
from ..metadata import load_metadata


def clear_database_tables(cursor):
    """Очищує всі таблиці перед імпортом даних
    
    Видаляє дані в правильному порядку (з урахуванням foreign keys):
    1. SkipRange (залежить від SkipSet)
    2. SkipSet (залежить від Episode)
    3. Episode (залежить від Season)
    4. Season (залежить від Series)
    5. Series (залежить від Media)
    6. MovieItem (залежить від Movie)
    7. Movie (залежить від Media)
    8. Xref_Tag2Media (залежить від Media та Tag)
    9. Media
    10. Tag
    """
    print("Clearing database tables...")
    
    tables_order = [
        'SkipRange',
        'SkipSet', 
        'Episode',
        'Season',
        'Series',
        'MovieItem',
        'Movie',
        'Xref_Tag2Media',
        'Media',
        'Tag'
    ]
    
    for table in tables_order:
        try:
            cursor.execute(f'DELETE FROM {table}')
            deleted_count = cursor.rowcount
            print(f"  Deleted {deleted_count} rows from {table}")
        except Exception as e:
            print(f"  Warning: Could not clear {table}: {e}")
    
    cursor.commit()
    print("Database tables cleared successfully.\n")
    return


def os_get_all_items_paths(paths):
    """Отримує всі шляхи до елементів з вказаних директорій"""
    items = []
    for path in paths:
        if not os.path.exists(path):
            continue
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                items.append(item_path)
    return items

def insert_movies_to_db(cursor):
    """Вставляє всі фільми з MOVIES_PATHS в БД"""
    paths = os_get_all_items_paths(MOVIES_PATHS)
    for path in tqdm(paths, desc="Inserting movies to DB"):
        insert_movie_collection_to_db(cursor, path)
    return

def insert_series_to_db(cursor):
    """Вставляє всі серіали з SERIES_PATHS в БД"""
    paths = os_get_all_items_paths(SERIES_PATHS)
    for path in tqdm(paths, desc="Inserting series to DB"):
        insert_serie_to_db(cursor, path)
    return

def transfer_timeToSkip_from_metadata(cursor):
    """Переносить timeToSkip з metadata в таблиці SkipSet та SkipRange
    
    Формат metadata:
    timeToSkip: [
        {"start": 100, "end": 200},
        {"start": 300, "end": 400}
    ]
    
    Кожен skip - це просто об'єкт з start та end (в мілісекундах)
    """
    metadata = load_metadata()
    
    jmesstr = r'series[].seasons[].files[?timeToSkip].{name: name, timeToSkip: timeToSkip}[]'
    timeToSkipSets = jmespath.search(jmesstr, metadata)
    
    if not timeToSkipSets:
        print("No timeToSkip data found in metadata.")
        return
    
    for item in tqdm(timeToSkipSets, desc="Transferring timeToSkip to DB"):
        episode_name = os.path.splitext(item['name'])[0]
        timeToSkip = item['timeToSkip']
        
        # Знаходимо episode_id в БД (без перевірки delD - шукаємо активні записи)
        cursor.execute('SELECT id FROM Episode WHERE title = ?', (episode_name,))
        result = cursor.fetchone()
        if result is None:
            print(f"Episode '{episode_name}' not found in DB. Skipping...")
            continue
        episode_id = result[0]
        
        # Вставляємо SkipSet
        skipset_id = insert_SkipSet_to_db(cursor, episode_id, source='METADATA', name='Default')
        if skipset_id is None:
            # SkipSet вже існує, пропускаємо
            continue
            
        # Вставляємо SkipRanges
        # Формат: [{"start": 100, "end": 200}, ...]
        for skip in timeToSkip:
            if not skip or not isinstance(skip, dict):
                print(f"Invalid skip range in episode '{episode_name}'. Skipping...")
                continue
            
            # В metadata немає label, тільки start та end
            start = skip.get('start')
            end = skip.get('end')
            
            if start is None or end is None:
                print(f"Missing start or end in skip range for episode '{episode_name}'. Skipping...")
                continue
                
            skipRange_id = insert_SkipRange_to_db(cursor, skipset_id, start, end, label='NULL')
    
    cursor.commit()
    print("TimeToSkip transfer completed.")
    return

def transfer_tags_from_metadata(cursor):
    """Переносить теги з metadata в таблиці Tag та Xref_Tag2Media"""
    metadata = load_metadata()
    
    jmesstr = r'*[?tags].{tags:tags[], title:title}[]'
    tagSets = jmespath.search(jmesstr, metadata)
    
    if not tagSets:
        print("No tags data found in metadata.")
        return
    
    # Створюємо словник тегів: {name: id}
    # Шукаємо всі теги (без перевірки delD - шукаємо активні записи)
    cursor.execute('SELECT id, name FROM Tag')
    tagsList = {row[1]: row[0] for row in cursor.fetchall()}
    
    for item in tqdm(tagSets, desc="Transferring tags to DB"):
        title = item['title']
        tags = item['tags']
        
        # Знаходимо media_id в БД (без перевірки delD - шукаємо активні записи)
        cursor.execute('SELECT id FROM Media WHERE title = ?', (title,))
        result = cursor.fetchone()
        if result is None:
            print(f"Media '{title}' not found in DB. Skipping...")
            continue
        media_id = result[0]
        
        # Додаємо кожен тег до media
        for tag in tags:
            if tag in tagsList:
                tag_id = tagsList[tag]
            else:
                # ✅ Створюємо новий тег
                tag_id = insert_Tag_to_db(cursor, tag)
                # Додаємо до словника, щоб не створювати знову
                tagsList[tag] = tag_id
                
            # Вставляємо зв'язок media-tag
            success = insert_Xref_Tag2Media_to_db(cursor, media_id, tag_id)
            if not success:
                # Зв'язок вже існує
                pass
    
    cursor.commit()
    print("Tags transfer completed.")
    return

def rebuild_database(cursor, clear_before=True):
    """Повністю перебудовує базу даних з файлової системи та metadata
    
    Args:
        cursor: Database cursor
        clear_before: Якщо True, очищує всі таблиці перед імпортом (за замовчуванням True)
    """
    print("Starting database rebuild...")
    
    # 0. Очищаємо таблиці (якщо потрібно)
    if clear_before:
        print("\n0. Clearing existing data...")
        clear_database_tables(cursor)
    
    # 1. Вставляємо фільми
    print("1. Inserting movies...")
    insert_movies_to_db(cursor)
    
    # 2. Вставляємо серіали
    print("\n2. Inserting series...")
    insert_series_to_db(cursor)
    
    # 3. Переносимо timeToSkip з metadata
    print("\n3. Transferring timeToSkip...")
    transfer_timeToSkip_from_metadata(cursor)
    
    # 4. Переносимо теги з metadata
    print("\n4. Transferring tags...")
    transfer_tags_from_metadata(cursor)
    
    print("\nDatabase rebuild completed successfully!")
    return


if __name__ == "__main__":
    conn = pyodbc.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        # Повна перебудова БД (з очищенням таблиць)
        rebuild_database(cursor, clear_before=True)
        
        # Або перебудова без очищення (додає до існуючих даних)
        # rebuild_database(cursor, clear_before=False)
        
        # Або викликаємо окремі функції за потреби:
        # clear_database_tables(cursor)
        # insert_movies_to_db(cursor)
        # insert_series_to_db(cursor)
        # transfer_timeToSkip_from_metadata(cursor)
        # transfer_tags_from_metadata(cursor)
        
    except Exception as e:
        print(f"\nError during database operations: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\nDatabase connection closed.")