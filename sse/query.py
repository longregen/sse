from .model import embed
from .db import get_similar_chunks

def query(settings, db_conn, query):
    embedding = embed(settings["embedding"]["query"] + query)
    res = get_similar_chunks(settings, db_conn, embedding)
    return res

