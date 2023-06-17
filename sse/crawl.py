import os
import json
import sys
import uuid
from datetime import datetime

from .db import store_embedding_db
from .get_sha256 import get_sha256
from .chunk_file import chunk_file
from .model import embed

def crawl(settings, db_conn, path):
    exclude = set(settings["crawl"]["exclude"])
    include = set(settings["crawl"]["include"])
    res = []

    if exclude is None:
        exclude = []
    if os.path.isfile(path) \
        and any(path.count(pattern) for pattern in include) \
        and all(not path.count(pattern) for pattern in exclude):
        res.append(process_file(settings, db_conn, path))

    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file_name in files:
                file_path = os.path.join(root, file_name)
                res.append(process_file(settings, db_conn, file_path))
    return res

def process_file(settings, db_conn, file_path):
    with open(file_path, "r", encoding='utf-8') as f:
        file_contents = f.read()
        content_hash = get_sha256(file_contents.encode('utf-8'))
        model_id = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

        cursor = db_conn.cursor()
        cursor.execute(f"SELECT * FROM source_embeddings WHERE content_hash='{content_hash}' AND model_id='{model_id}'")
        data = cursor.fetchone()

        if data is None:
            return [file_path, process_contents(settings, db_conn, file_path, file_contents, content_hash, model_id)]
        else:
            print(f'file {file_path} already in db: {data[0]} - {data[1]}, skipping', file=sys.stderr)

def process_contents(settings, db_conn, file_path, file_contents, content_hash, model_id):
    project = settings["project"]["name"]
    chunks = chunk_file(settings, file_contents)
    created_at = datetime.now()
    store_embedding_db(db_conn, "source_embeddings", [content_hash, project, model_id, created_at])
    id = str(uuid.uuid4())
    abs_path = os.path.abspath(file_path)
    store_embedding_db(db_conn, "file_info", [id, project, abs_path, content_hash, created_at])
    res = []
    for source_chunk_index, chunk_data in enumerate(chunks):
        chunk_hash = get_sha256(chunk_data.encode('utf-8'))
        chunk_embedding = embed(settings["embedding"]["store"] + chunk_data)
        if len(chunk_embedding) < 0:
            print(f'file {file_path} has len(chunk_embedding) = {len(chunk_embedding)}, skipping')
            continue
        created_at = datetime.now()
        id = str(uuid.uuid4())
        data = [
            id,
            model_id,
            project,
            chunk_hash,
            chunk_data,
            f"[{','.join([str(x) for x in chunk_embedding])}]",
            content_hash,
            source_chunk_index,
            created_at
        ]
        store_embedding_db(db_conn, "chunk_embedding", data)
        res.append(data)
    return res

