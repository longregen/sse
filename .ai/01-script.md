Model: GPT-4
User
`llama-edge` runs the following algorithm:

```pseudocode
let $SRC be the repository with the source code
let $EMBEDDING_FAMILY be a family of algorithms for embeddings generation, for example, 'llama:wizard-vicuna:lora-adapted'
let $EMBEDDING_MODEL be a unique identifier of the embedding system, for example 'lora:2023.06.24-run2:gpqt-4bit-gs128:{zbase32 sha256}'
let $EMBEDDING be $EMBEDDING_FAMILY concatenated with ":" and $EMBEDDING_MODEL
let $DB be a sqlite database stored

let $SETTINGS be the JSON parsing of file ~/.config/llama-edge.json or, if the file doesn't exist, use {
  embedding: {
    family: "llama:guanaco-33B",
    model: "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
    style: "chunked-2048",
    binary_path: "embedding",
    args: "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
    tokenization_length: 2048
  }
}
for each $FILE in $SRC:
  let $CONTENTS be the contents of the $FILE
  let $SHASUM be the sha256 sum of $CONTENTS, zbase32 encoded
  let $EMBEDDING be $SETTINGS.embedding.{family:model:style}
  # in this example, it will be the string "llama:guanaco-33B:ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy:chunked-2048"
  check $DB, table "source_embeddings", if an entry exists for hash=$SHASUM and embedding=$EMBEDDING
  if it doesn't exist:
    let $CHUNKS be the tokenization in chunks of size $TOKENIZATION_LENGTH of the contents of $FILE
    for each $CHUNK in $CHUNKS:
        let $DATE be the current timestamp from UNIX epoch in milliseconds
        let $CHUNK_DATA be the binary representation that fits in $TOKENIZATION_LENGTH tokenization
        let $CHUNK_HASH be the hash of $CHUNK_DATA
        let $CHUNK_EMBEDDING be the result of running $SETTINGS.embedding.binary_path on $CHUNK_DATA 
        store in $DB, table "chunk_embedding", fields $CHUNK_DATA, $CHUNK_HASH, $CHUNK_EMBEDDING, $SHASUM, $DATE
    store in $DB, table "source_embeddings", the entry with hash=$SHASUM and embedding=$EMBEDDING
```
Can you code this for me?
ChatGPT

Sure, it seems like you are asking for a script that handles code repository embedding generation. Here's a Python version of your pseudocode that might meet your needs:

python

import os
import json
import hashlib
import sqlite3
import subprocess
from pathlib import Path

def load_settings():
    settings_path = Path("~/.config/llama-edge.json").expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "llama:guanaco-33B",
                "model": "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
                "style": "chunked-2048",
                "binary_path": "embedding",
                "args": "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
                "tokenization_length": 2048
            }
        }

def chunk_file(file_contents, chunk_size):
    return [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return hasher.digest().encode("zbase32")

def compute_embedding(settings, chunk_data):
    binary_path = settings["embedding"]["binary_path"]
    args = settings["embedding"]["args"].replace("$HOME", os.getenv("HOME"))
    cmd = f"{binary_path} {args}"
    result = subprocess.run(cmd, input=chunk_data, text=True, capture_output=True)
    return result.stdout

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)"
    db_conn.execute(query, fields)
    db_conn.commit()

def main():
    settings = load_settings()
    SRC = "source_directory"  # Replace with your source directory
    DB_PATH = "llama-edge.db"  # Replace with your DB path
    db_conn = sqlite3.connect(DB_PATH)
    
    for root, dirs, files in os.walk(SRC):
        for file_name in files:
            with open(os.path.join(root, file_name), "rb") as f:
                file_contents = f.read()
                sha_sum = get_sha256(file_contents)
                embedding = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE hash='{sha_sum}' AND embedding='{embedding}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                    for chunk in chunks:
                        date = int(time.time() * 1000)
                        chunk_data = chunk.encode('utf-8')
                        chunk_hash = get_sha256(chunk_data)
                        chunk_embedding = compute_embedding(settings, chunk_data)
                        store_embedding_db(db_conn, "chunk_embedding", [chunk_data, chunk_hash, chunk_embedding, sha_sum, date])
                    store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

    db_conn.close()

if __name__ == "__main__":
    main()

This script assumes that you have sqlite3 installed on your system, that the specified database exists, and that the specified tables ("source_embeddings" and "chunk_embedding") already exist in the database. You will also need to replace "source_directory" and
User
Please also create the tables if they don't exist
ChatGPT

Sure, let's add functionality to create the tables if they don't exist. Here's the revised code:

python

import os
import json
import hashlib
import sqlite3
import subprocess
from pathlib import Path
import time

def load_settings():
    settings_path = Path("~/.config/llama-edge.json").expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "llama:guanaco-33B",
                "model": "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
                "style": "chunked-2048",
                "binary_path": "embedding",
                "args": "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
                "tokenization_length": 2048
            }
        }

def chunk_file(file_contents, chunk_size):
    return [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return hasher.digest().encode("zbase32")

def compute_embedding(settings, chunk_data):
    binary_path = settings["embedding"]["binary_path"]
    args = settings["embedding"]["args"].replace("$HOME", os.getenv("HOME"))
    cmd = f"{binary_path} {args}"
    result = subprocess.run(cmd, input=chunk_data, text=True, capture_output=True)
    return result.stdout

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)"
    db_conn.execute(query, fields)
    db_conn.commit()

def create_tables_if_not_exists(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            hash TEXT,
            embedding TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            chunk_data BLOB,
            chunk_hash TEXT,
            chunk_embedding TEXT,
            shasum TEXT,
            date INTEGER
        )
    """)

    db_conn.commit()

def main():
    settings = load_settings()
    SRC = "source_directory"  # Replace with your source directory
    DB_PATH = "llama-edge.db"  # Replace with your DB path
    db_conn = sqlite3.connect(DB_PATH)
    create_tables_if_not_exists(db_conn)

    for root, dirs, files in os.walk(SRC):
        for file_name in files:
            with open(os.path.join(root, file_name), "rb") as f:
                file_contents = f.read()
                sha_sum = get_sha256(file_contents)
                embedding = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE hash='{sha_sum}' AND embedding='{embedding}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                    for chunk in chunks:
                        date = int(time.time() * 1000)
                        chunk_data = chunk.encode('utf-8')
                        chunk_hash = get_sha256(chunk_data)
                        chunk_embedding = compute_embedding(settings, chunk_data)
                        store_embedding_db(db_conn, "chunk_embedding", [chunk_data, chunk_hash, chunk_embedding, sha_sum, date])
                    store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

    db_conn.close()

if __name__ == "__main__":
    main()

This code will now create the "source_embeddings" and "chunk_embedding" tables if they do not already exist in the database. Please ensure you have the necessary permissions to create tables in your database. As before, replace "source_directory" and "llama-edge.db" with your actual source directory and database path.
User
I'm getting this error: 
return hasher.digest().encode("zbase32")     ■ Cannot access member "encode" for type "bytes"    Member "encode" is unknown
Can you fix it?
ChatGPT

I'm sorry for the confusion. The hashlib's digest() method indeed returns a bytes object, and bytes object doesn't have encode() method. Also, the Python standard library does not support zbase32 encoding out of the box.

You can use the base64 module for base32 encoding, or install a third-party library like base58 for zbase32 encoding.

Here is the code modified to use base32 encoding:

python

import os
import json
import hashlib
import sqlite3
import subprocess
from pathlib import Path
import time
import base64

def load_settings():
    settings_path = Path("~/.config/llama-edge.json").expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "llama:guanaco-33B",
                "model": "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
                "style": "chunked-2048",
                "binary_path": "embedding",
                "args": "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
                "tokenization_length": 2048
            }
        }

def chunk_file(file_contents, chunk_size):
    return [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return base64.b32encode(hasher.digest()).decode()

def compute_embedding(settings, chunk_data):
    binary_path = settings["embedding"]["binary_path"]
    args = settings["embedding"]["args"].replace("$HOME", os.getenv("HOME"))
    cmd = f"{binary_path} {args}"
    result = subprocess.run(cmd, input=chunk_data, text=True, capture_output=True)
    return result.stdout

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)"
    db_conn.execute(query, fields)
    db_conn.commit()

def create_tables_if_not_exists(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            hash TEXT,
            embedding TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            chunk_data BLOB,
            chunk_hash TEXT,
            chunk_embedding TEXT,
            shasum TEXT,
            date INTEGER
        )
    """)

    db_conn.commit()

def main():
    settings = load_settings()
    SRC = "source_directory"  # Replace with your source directory
    DB_PATH = "llama-edge.db"  # Replace with your DB path
    db_conn = sqlite3.connect(DB_PATH)
    create_tables_if_not_exists(db_conn)

    for root, dirs, files in os.walk(SRC):
        for file_name in files:
            with open(os.path.join(root, file_name), "rb") as f:
                file_contents = f.read()
                sha_sum = get_sha256(file_contents)
                embedding = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE hash='{sha_sum}' AND embedding='{embedding}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                    for chunk in chunks:
                        date = int(time.time() * 1000)
                        chunk_data = chunk.encode('utf-8')
                        chunk_hash = get_sha256(chunk_data)
                        chunk_embedding = compute_embedding(settings, chunk_data)
                        store_embedding_db(db_conn, "chunk_embedding", [chunk_data, chunk_hash, chunk_embedding, sha_sum, date])
                    store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

    db_conn.close()

if __name__ == "__main__":
    main()

Remember to replace "source_directory" and "llama-edge.db" with your actual source directory and database path.
User
I'm getting a FileNotFoundError: [Errno 2] No such file or directory: 'embedding -m models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin' problem. Can you use a different subprocess method that split the arguments?
ChatGPT

I apologize for the confusion. The subprocess module has different ways to take arguments. If you pass them as a single string (like I did in my previous response), you need to set shell=True in the subprocess.run() call. However, this could be a security hazard if you're dealing with untrusted input.

A better way is to pass the command and its arguments as a list, like this:

python

import os
import json
import hashlib
import sqlite3
import subprocess
from pathlib import Path
import time
import base64

def load_settings():
    settings_path = Path("~/.config/llama-edge.json").expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "llama:guanaco-33B",
                "model": "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
                "style": "chunked-2048",
                "binary_path": "embedding",
                "args": "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
                "tokenization_length": 2048
            }
        }

def chunk_file(file_contents, chunk_size):
    return [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return base64.b32encode(hasher.digest()).decode()

def compute_embedding(settings, chunk_data):
    binary_path = settings["embedding"]["binary_path"]
    args = settings["embedding"]["args"].replace("$HOME", os.getenv("HOME"))
    cmd = [binary_path] + args.split()
    result = subprocess.run(cmd, input=chunk_data, text=True, capture_output=True)
    return result.stdout

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)"
    db_conn.execute(query, fields)
    db_conn.commit()

def create_tables_if_not_exists(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            hash TEXT,
            embedding TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            chunk_data BLOB,
            chunk_hash TEXT,
            chunk_embedding TEXT,
            shasum TEXT,
            date INTEGER
        )
    """)

    db_conn.commit()

def main():
    settings = load_settings()
    SRC = "source_directory"  # Replace with your source directory
    DB_PATH = "llama-edge.db"  # Replace with your DB path
    db_conn = sqlite3.connect(DB_PATH)
    create_tables_if_not_exists(db_conn)

    for root, dirs, files in os.walk(SRC):
        for file_name in files:
            with open(os.path.join(root, file_name), "rb") as f:
                file_contents = f.read()
                sha_sum = get_sha256(file_contents)
                embedding = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE hash='{sha_sum}' AND embedding='{embedding}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                   

User
Great, but now, I get this error:

sqlite3.OperationalError: table source_embeddings has 2 columns but 5 values were supplied

This is the current code:

```
import os
import json
import hashlib
import sqlite3
import subprocess
from pathlib import Path
import time
import base64

def load_settings():
    settings_path = Path("~/.config/llama-edge.json").expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "llama:guanaco-33B",
                "model": "ggmlv3.q5_1:i4u61txppq83d4pjekk48bjjn3ne3wmr5judw7xqjahhiuatzujy",
                "style": "chunked-2048",
                "binary_path": "embedding",
                "args": "-m $HOME/models/guanaco-33B-GGML/guanaco-33B.ggmlv3.q5_1.bin",
                "tokenization_length": 2048
            }
        }

def chunk_file(file_contents, chunk_size):
    return [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return base64.b32encode(hasher.digest()).decode()

def compute_embedding(settings, chunk_data):
    binary_path = settings["embedding"]["binary_path"]
    args = settings["embedding"]["args"].replace("$HOME", os.getenv("HOME"))
    cmd = [binary_path] + args.split()
    result = subprocess.run(cmd, input=chunk_data, text=True, capture_output=True)
    return result.stdout

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)"
    db_conn.execute(query, fields)
    db_conn.commit()

def create_tables_if_not_exists(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            hash TEXT,
            embedding TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            chunk_data BLOB,
            chunk_hash TEXT,
            chunk_embedding TEXT,
            shasum TEXT,
            date INTEGER
        )
    """)

    db_conn.commit()

def main():
    settings = load_settings()
    SRC = "../alicia/src/utils"  # Replace with your source directory
    DB_PATH = "llama-edge.db"  # Replace with your DB path
    db_conn = sqlite3.connect(DB_PATH)
    create_tables_if_not_exists(db_conn)

    for root, dirs, files in os.walk(SRC):
        for file_name in files:
            with open(os.path.join(root, file_name), "rb") as f:
                print(f'working on {file_name}')
                file_contents = f.read()
                sha_sum = get_sha256(file_contents)
                embedding = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE hash='{sha_sum}' AND embedding='{embedding}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                    for chunk_data in chunks:
                        date = int(time.time() * 1000)
                        chunk_hash = get_sha256(chunk_data)
                        chunk_embedding = compute_embedding(settings, chunk_data.decode('utf-8'))
                        store_embedding_db(db_conn, "chunk_embedding", [chunk_data, chunk_hash, chunk_embedding, sha_sum, date])
                    store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

    db_conn.close()

if __name__ == "__main__":
    main()

```

What could be happening?
ChatGPT

The error message "table source_embeddings has 2 columns but 5 values were supplied" is raised because the number of values you're trying to insert into your "source_embeddings" table is greater than the number of columns that exist in the table.

The table "source_embeddings" was created with only 2 columns, 'hash' and 'embedding'. However, when inserting data into "source_embeddings", you are supplying 5 values. This discrepancy is causing the OperationalError.

Here's how you can fix it:

    Correct the field values passed to store_embedding_db() when you're inserting into "source_embeddings".

python

# Wrong
store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

# Correct
store_embedding_db(db_conn, "source_embeddings", [sha_sum, embedding])

    Update the store_embedding_db() function to take into account the different number of columns for different tables. For "source_embeddings", you'll only need to supply 2 values.

python

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in fields])})"
    db_conn.execute(query, fields)
    db_conn.commit()

This version of store_embedding_db() constructs an SQL query with a number of placeholders ('?') equal to the number of fields, so it can be used with any number of values.
