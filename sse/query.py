from .model import embed
from .db import get_similar_chunks

def query(settings, db_conn, query, extra_params):
    embedding = embed(settings["embedding"]["query"] + query)
    res = get_similar_chunks(settings, db_conn, embedding, extra_params)
    return res

