import psycopg2
import sys

def get_conn(settings):
    DB_NAME = settings["database"]["name"]
    DB_USER = settings["database"]["user"]
    DB_PASS = settings["database"]["password"]
    DB_HOST = settings["database"]["host"]
    DB_PORT = settings["database"]["port"]

    print('» connecting to db...', file=sys.stderr)
    db_conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    create_tables_if_not_exists(db_conn)
    print ('» connected to db OK', file=sys.stderr)
    return db_conn

def create_tables_if_not_exists(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_embeddings (
            content_hash TEXT PRIMARY KEY,
            project TEXT,
            model_id TEXT,
            created_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_info (
            id UUID PRIMARY KEY,
            project TEXT,
            file_path TEXT,
            content_hash TEXT REFERENCES source_embeddings(content_hash),
            created_at TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunk_embedding (
            id UUID PRIMARY KEY,
            model_id TEXT,
            project TEXT,
            chunk_hash TEXT,
            chunk_data TEXT,
            chunk_embedding vector(1024),
            source_hash TEXT REFERENCES source_embeddings(content_hash),
            source_chunk_index INTEGER,
            created_at TIMESTAMP
        )
    """)

    db_conn.commit()

def store_embedding_db(db_conn, table_name, fields):
    query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s' for _ in fields])})"
    with db_conn.cursor() as cursor:
        cursor.execute(query, fields)
    db_conn.commit()

def get_similar_chunks(settings, db_conn, embedding):
    project = settings["project"]["name"]
    limit = settings["query"]["limit"]
    cursor = db_conn.cursor()
    query = """
        WITH similar_chunks AS (
            SELECT id, source_chunk_index, source_hash, chunk_data, chunk_embedding <-> %s as vector_distance
            FROM chunk_embedding
            WHERE project = %s
            ORDER BY vector_distance ASC
        )
        SELECT 
            file_info.id, 
            file_info.file_path, 
            file_info.content_hash, 
            file_info.created_at, 
            source_embeddings.model_id,
            array_agg(similar_chunks.source_chunk_index) as matched_chunk_indices,
            array_agg(similar_chunks.chunk_data) as matched_chunk_indices,
            avg(similar_chunks.vector_distance) as avg_vector_distance,
            min(similar_chunks.vector_distance) as min_vector_distance
        FROM file_info
        JOIN source_embeddings ON source_embeddings.content_hash = file_info.content_hash
        JOIN similar_chunks ON file_info.content_hash = similar_chunks.source_hash
        WHERE file_info.project = %s
        GROUP BY 
            file_info.id, 
            file_info.file_path, 
            file_info.content_hash, 
            file_info.created_at, 
            source_embeddings.model_id
        ORDER BY min_vector_distance ASC
        LIMIT %s
    """
    cursor.execute(query, (
        f"[{','.join([str(x) for x in embedding])}]",
        project,
        project,
        limit
    ))
    return cursor.fetchall()
