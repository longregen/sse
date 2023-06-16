from pathlib import Path
import json
import os

def load_settings():
    path = os.environ['SSE_CONFIG'] if "SSE_CONFIG" in os.environ else "~/.config/sse.json"
    settings_path = Path(path).expanduser()
    if settings_path.exists():
        with open(settings_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "embedding": {
                "family": "hf:intfloat/e5-large-v2",
                "model": "githash:d94960066016d2064f2a3a2dbc65107a2b48230d",
                "style": "chunked-512",
                "max_length": 512,
                "store": "passage: ",
                "query": "query: ",
            },
            "database": {
                "name": "datastore",
                "user": "datastore",
                "password": "password",
                "host": "localhost",
                "port": "5432"
            },
            "crawl": {
                "exclude": ["package-lock.json", "package.json", "node_modules", ".gitignore"],
                "include": ["py" "ts", "js", "json", "md", "tsx", "jsx" "txt"]
            },
            "server": {
                "daemonize": "start",
                "host": "127.0.0.1",
                "port": 5001,
            },
            "project": {}
        }

