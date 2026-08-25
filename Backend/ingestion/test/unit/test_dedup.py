import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Converter.dedup import compute_content_hash


def test_computes_sha256_hash():
    data = b"some photo bytes"
    assert compute_content_hash(data) == hashlib.sha256(data).hexdigest()


def test_same_bytes_produce_same_hash():
    data = b"identical content"
    assert compute_content_hash(data) == compute_content_hash(data)


def test_different_bytes_produce_different_hash():
    assert compute_content_hash(b"one") != compute_content_hash(b"two")
