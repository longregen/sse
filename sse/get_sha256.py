import hashlib
import base64

def get_sha256(content):
    hasher = hashlib.sha256(content)
    return base64.b32encode(hasher.digest()).decode()
