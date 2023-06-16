import sys
from .model import tokenizer

def chunk_file(settings, file_contents):
    i = 0
    chunks = []
    while i + 1 < len(file_contents):
        tokenization = tokenizer(
            settings["embedding"]["store"] + file_contents[i:],
            max_length = settings["embedding"]["max_length"],
            return_offsets_mapping=True,
            truncation='only_first'
        )
        if len(tokenization.offset_mapping) < 2 or len(tokenization.offset_mapping[-2]) < 1:
            break
        end = tokenization.offset_mapping[-2][1]
        chunks.append(file_contents[i:i+end])
        i = i + end
    print(f'» split into {len(chunks)} chunks', file=sys.stderr)
    return chunks
