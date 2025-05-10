import os, shutil
import sqlite3
from random import randrange
from PIL import  Image
from datetime import datetime
import base64

con = sqlite3.connect('mydatabase.db', check_same_thread=False)
cursor = con.cursor()
THUMBNAIL_PATH = 'media_cache/thumbnail/'

def random_id():
    return randrange(1000)

def format_cursor(cur):
    res = []
    for row in cur:
        payload = {
            'id': row[0],
            'name': row[1],
            'locations': row[3].split(',') if row[3] else [],
            'tags': row[4].split(',') if row[4] else [],
            'date': row[5],
            'description': row[6]
        }
        res.append(payload)
    return res

def insert_media(data):
    sql = """
    INSERT INTO media_t (media_name, media_obj, locations, tags, date_created, description)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (
        data.get('name'),
        None,
        ','.join(data.get('locations', [])),
        ','.join(data.get('tags', [])),
        data.get('date'),
        data.get('description')
    ))
    con.commit()
    return cursor.lastrowid

def get_all_media():
    sql = "SELECT * FROM media_t ORDER BY media_id DESC"
    return cursor.execute(sql)

def get_media_id(media_id):
    sql = "SELECT * FROM media_t WHERE media_id = ?"
    return cursor.execute(sql, (media_id,))

def search(name=None, tag=None, typ=None, location=None, date=None):
    sql = "SELECT * FROM media_t WHERE 1=1"
    params = []
    if name:
        sql += " AND media_name LIKE ?"
        params.append(f"%{name}%")
    if tag:
        sql += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    if location:
        sql += " AND locations LIKE ?"
        params.append(f"%{location}%")
    if date:
        sql += " AND date_created = ?"
        params.append(date)
    return cursor.execute(sql, params)

def delete_by_id(media_id):
    sql = "DELETE FROM media_t WHERE media_id = ?"
    cursor.execute(sql, (media_id,))
    con.commit()

def get_blob_obj(media_id):
    sql = "SELECT media_obj FROM media_t WHERE media_id = ?"
    cursor.execute(sql, (media_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def update_by_id(data):
    sql = """
    UPDATE media_t SET media_name = ?, locations = ?, tags = ?, date_created = ?, description = ? WHERE media_id = ?
    """
    cursor.execute(sql, (
        data.get('name'),
        ','.join(data.get('locations', [])),
        ','.join(data.get('tags', [])),
        data.get('date'),
        data.get('description'),
        data.get('id')
    ))
    con.commit()

def get_media_name(media_id):
    sql = "SELECT media_name FROM media_t WHERE media_id = ?"
    cursor.execute(sql, (media_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def rename_by_id(file_name, media_id):
    ext = file_name.split('.')[-1]
    return f'{media_id}.{ext}'

def gen_thumbnail(name):
    path = 'media_cache/temp/' + name
    im = Image.open(path)
    im.thumbnail((300, 300))
    if not os.path.exists(THUMBNAIL_PATH):
        os.makedirs(THUMBNAIL_PATH, exist_ok=True)
    im.save(os.path.join(THUMBNAIL_PATH, name))

def update_media_obj(media_id, content):
    sql = "UPDATE media_t SET media_obj = ? WHERE media_id = ?"
    cursor.execute(sql, (content, media_id))
    con.commit()

async def get_media_object(media_id):
    sql = "SELECT media_obj, media_name FROM media_t WHERE media_id = ?"
    cursor.execute(sql, (media_id,))
    row = cursor.fetchone()
    if row and row[0]:
        write_file(row[0], row[1])
        return row[1]
    return None

def write_file(file_bytes, name):
    path = 'media_cache/temp'
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, name), 'wb') as f:
        f.write(file_bytes)

def is_image(file_name):
    ext = file_name.split('.')[-1]
    return ext in ['jpg','bmp','gif','avif','png']

def cache_image_by_id(media_id):
    media_obj = get_blob_obj(media_id)
    media_name = get_media_name(media_id)
    if media_obj and is_image(media_name):
        new_name = rename_by_id(media_name, media_id)
        write_file(media_obj, new_name)
        gen_thumbnail(new_name)

def clear_temp():
    folder = 'media_cache/temp'
    if not os.path.exists(folder):
        return
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def main():
    print('test from main')
    clear_temp()

if __name__ == '__main__':
    main()