# sse: semantic search on the edge

Query your documents finding semantic similarities.

## Usage

```
sse crawl <project> <dir> [--include pattern] [--exclude pattern]
    - Crawls the given project directory, including or excluding files that match certain patterns.

sse query <project> <query> [--limit number]
    - Runs a query on a specific project.

sse help
    - Displays this help message.
```

## Example response

```
sse query hammurabi 'how to render an avatar'
  src/lib/babylon/avatars/AvatarRenderer.ts [distance 12.820]
  src/lib/babylon/avatar-rendering-system.ts [distance 13.001]
  src/lib/babylon/avatars/adr-65/customizations.ts [distance 13.209]
```

## Setup

**Warning: the status of the project is very early alpha**

1. Create a database in postgresql with the pgvector extension, for example, by running this:
```
CREATE ROLE datastore WITH LOGIN PASSWORD 'password' CREATEDB;
CREATE DATABASE datastore;
GRANT ALL PRIVILEGES ON DATABASE datastore TO datastore;
CREATE EXTENSION IF NOT EXISTS vector;
```
2. Modify `sse/load_settings.py` to your liking
3. Install dependencies: `pip install psycopg2 requests flask`
4. Alias main.py to be `sse` in your path

## Indexing folders

Usage: `sse crawl <project> <dir>`, for example, `sse crawl my-project ~/Notes`. To index documents, `sse` runs the following algorithm:

```pseudocode
let $SETTINGS be the JSON parsing of file ~/.config/sse.json or the unix env variable $SSE_CONFIG 
let $DB be a connection to a postgresql database defined in $SETTINGS
Create tables "source_embeddings", "file_info", and "chunk_embedding" if they do not exist in $DB

for each $FILE in $SRC:
  let $CONTENTS be the contents of the $FILE
  let $SHASUM be the sha256 sum of $CONTENTS, base32 encoded
  let $ABS_PATH be the absolute path of $FILE
  let $MODEL_ID be the embedding model id defined in $SETTINGS
  let $CHUNKS be the tokenization of the contents of $FILE into chunks of size determined by the model's tokenizer
  let $DATE be the current timestamp
  store $SHASUM, $MODEL_ID, $DATE in table "source_embeddings"
  store unique id, $ABS_PATH, $SHASUM, $DATE in table "file_info"
  for each $CHUNK in $CHUNKS:
    let $CHUNK_HASH be the sha256 sum of $CHUNK, base32 encoded
    let $CHUNK_EMBEDDING be the result of running the embedding model on $CHUNK
    store unique id, $MODEL_ID, $CHUNK_HASH, $CHUNK, $CHUNK_EMBEDDING, $SHASUM, the index of $CHUNK in $CHUNKS, $DATE in table "chunk_embedding"
```

## Dependencies
- [e5-large-v2](https://huggingface.co/intfloat/e5-large-v2), torch
- [psycopg2](https://pypi.org/project/psycopg2/)
- [pgvector](https://github.com/pgvector/pgvector)
- "CREATE EXTENSION vector;" in the DB

