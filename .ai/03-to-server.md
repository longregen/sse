Can you convert this code?
```
def main():
    parser = argparse.ArgumentParser(description="llama-edge: embeddings generation script")
    parser.add_argument("src", help="path to the source code directory.")
    args = parser.parse_args()
    SRC = args.src

    settings = load_settings()

    DB_NAME = settings["database"]["name"]
    DB_USER = settings["database"]["user"]
    DB_PASS = settings["database"]["password"]
    DB_HOST = settings["database"]["host"]
    DB_PORT = settings["database"]["port"]

    print('» connecting to db...', file=sys.stderr)
    db_conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    create_tables_if_not_exists(db_conn)
    print ('» connected to db OK', file=sys.stderr)
    for root, _, files in os.walk(SRC):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, "rb") as f:
                print(f'» working on {file_path}', file=sys.stderr)
                file_contents = f.read()
                content_hash = get_sha256(file_contents)
                model_id = f'{settings["embedding"]["family"]}:{settings["embedding"]["model"]}:{settings["embedding"]["style"]}'

                cursor = db_conn.cursor()
                cursor.execute(f"SELECT * FROM source_embeddings WHERE content_hash='{content_hash}' AND model_id='{model_id}'")
                data = cursor.fetchone()

                if data is None:
                    chunks = chunk_file(file_contents, settings["embedding"]["tokenization_length"])
                    created_at = datetime.now()
                    store_embedding_db(db_conn, "source_embeddings", [content_hash, model_id, created_at])
                    id = str(uuid.uuid4())
                    abs_path = os.path.abspath(file_path)
                    store_embedding_db(db_conn, "file_info", [id, abs_path, content_hash, created_at])
                    for chunk_data in chunks:
                        chunk_hash = get_sha256(chunk_data)
                        chunk_embedding = compute_embedding(chunk_data.decode('utf-8'))
                        if len(chunk_embedding) > 0:
                            created_at = datetime.now()
                            id = str(uuid.uuid4())
                            store_embedding_db(
                                db_conn,
                                "chunk_embedding",
                                [
                                    id,
                                    model_id,
                                    chunk_hash,
                                    chunk_data,
                                    f"[{','.join([f'{x:.4}' for x in chunk_embedding])}]",
                                    content_hash,
                                    created_at
                                ]
                            )

    db_conn.close()
```

So that instead of being executed on the command line, it runs a small flask server with one endpoint named "/generate" that takes two strings over the POST of a JSON ("query" and "data") and returns a "result", "/crawl" that takes two strings over the POST of a JSON ("query" and "directory", optionally "exclude" (an array of strings) and "include" (an array of strings)), "/query" which returns the search over chunks and returns file information based on these tables:
```

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            content_hash TEXT PRIMARY KEY,
            model_id TEXT,
            created_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_info (
            id UUID PRIMARY KEY,
            file_path TEXT,
            content_hash TEXT REFERENCES source_embeddings(content_hash),
            created_at TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            id UUID PRIMARY KEY,
            model_id TEXT,
            chunk_hash BYTEA,
            chunk_data TEXT,
            chunk_embedding vector(768),
            source_hash TEXT REFERENCES source_embeddings(content_hash),
            created_at TIMESTAMP
        )
    """)
```
