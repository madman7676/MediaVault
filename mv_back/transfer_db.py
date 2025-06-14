import json
import pyodbc
from tqdm import tqdm
from datetime import datetime

from metadata import load_metadata
from config import *

conn = pyodbc.connect(DB_CONNECTION_STRING)
cursor = conn.cursor()

metadata = load_metadata()

# Вставка у Media → MediaUnit → Episode → TimeToSkip → Tag → MediaTag
inserted_series = 0
inserted_parts = 0
tags_dict = {}

all_items = metadata.get("series", []) + metadata.get("movies", [])

for item in tqdm(all_items, desc="Transfer to DB"):  # Додаємо tqdm
    media_id = item["id"]
    title = item["title"]
    path = item["path"]
    auto_added = int(item.get("auto_added", False))
    # last_modified = item.get("last_modified")
    media_type = item["type"]

    raw_ts = item.get("last_modified")
    if raw_ts:
        try:
            last_modified = datetime.fromisoformat(raw_ts)
        except ValueError:
            last_modified = None
    else:
        last_modified = None

    
    # Insert into Media
    cursor.execute("""
        INSERT INTO Media (id, title, path, auto_added, last_modified, type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, media_id, title, path, auto_added, last_modified, media_type)

    # Tags
    for tag in item.get("tags", []):
        if tag not in tags_dict:
            cursor.execute("SELECT id FROM Tag WHERE name = ?", tag)
            row = cursor.fetchone()
            if row:
                tag_id = row[0]
            else:
                cursor.execute("INSERT INTO Tag (name) OUTPUT INSERTED.id VALUES (?)", tag)
                tag_id = cursor.fetchone()[0]
            tags_dict[tag] = tag_id
        else:
            tag_id = tags_dict[tag]

        cursor.execute("INSERT INTO MediaTag (media_id, tag_id) VALUES (?, ?)", media_id, tag_id)

    if media_type == "series":
        for season in item.get("seasons", []):
            unit_title = season["title"]
            unit_path = season["path"]

            cursor.execute("""
                INSERT INTO MediaUnit (media_id, title, path, has_episodes, unit_type)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, 1, 'season')
            """, media_id, unit_title, unit_path)
            media_unit_id = cursor.fetchone()[0]

            for file in season.get("files", []):
                episode_name = file["name"]
                cursor.execute("""
                    INSERT INTO Episode (media_unit_id, name)
                    OUTPUT INSERTED.id
                    VALUES (?, ?)
                """, media_unit_id, episode_name)
                episode_id = cursor.fetchone()[0]

                for skip in file.get("timeToSkip", []):
                    cursor.execute("""
                        INSERT INTO TimeToSkip (episode_id, start_time, end_time)
                        VALUES (?, ?, ?)
                    """, episode_id, skip["start"], skip["end"])
            inserted_series += 1
    elif media_type == "collection":
        for part in item.get("parts", []):
            cursor.execute("""
                INSERT INTO MediaUnit (media_id, title, path, has_episodes, unit_type)
                VALUES (?, ?, ?, 0, 'part')
            """, media_id, part["title"], part["path"])
        inserted_parts += 1

conn.commit()
cursor.close()
conn.close()

(inserted_series, inserted_parts, len(tags_dict))
