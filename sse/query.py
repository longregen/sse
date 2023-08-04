import requests
from .db import get_similar_chunks

def query(settings, db_conn, query, extra_params):
    if settings["embedding"]["local"]:
        from .model import embed
        embedding = embed(settings["embedding"]["query"] + query)
    else:
        response = requests.post(
            settings["embedding"]["url"],
            json={"prompt": settings["embedding"]["query"] + query}
        )
        embedding = response.json()
    res = get_similar_chunks(settings, db_conn, embedding, extra_params)
    return res

