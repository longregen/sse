from flask import Flask, request

from .query import query
from .crawl import crawl
from .db import get_conn
from .load_settings import load_settings

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def get_health():
    return {"status": "ok"}

@app.route('/crawl', methods=['POST'])
def post_crawl():
    project = request.json.get('project')
    directory = request.json.get('dir')
    includes = request.json.get('include', [])
    excludes = request.json.get('exclude', [])

    settings = load_settings()
    if "project" not in settings:
        settings["project"] = {}
    db_conn = get_conn(settings)

    settings["project"]["name"] = project
    for x in includes:
        settings["crawl"]["include"].append(x)
    for x in excludes:
        settings["crawl"]["exclude"].append(x)
    crawl(settings, db_conn, directory)
    return {"status": "completed"}

@app.route('/query', methods=['POST'])
def post_query():
    project = request.json.get('project')
    query_string = request.json.get('query')
    limit = request.json.get('limit', 5)

    settings = load_settings()
    if "project" not in settings:
        settings["project"] = {}
    if "query" not in settings:
        settings["query"] = {}
    db_conn = get_conn(settings)

    settings["project"]["name"] = project
    settings["query"]["limit"] = limit
    return {"status": "completed", "result": query(settings, db_conn, query_string)}

def run_server(host: str, port: int):
    app.run(host=host, port=port)

