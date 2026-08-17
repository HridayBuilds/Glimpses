import hashlib


def compute_content_hash(data):
    return hashlib.sha256(data).hexdigest()
