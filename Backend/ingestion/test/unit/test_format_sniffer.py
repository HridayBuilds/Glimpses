import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Converter.format_sniffer import sniff_format


def test_sniffs_jpeg():
    assert sniff_format(b"\xff\xd8\xff\xe0rest") == "jpeg"


def test_sniffs_png():
    assert sniff_format(b"\x89PNG\r\n\x1a\nrest") == "png"


def test_sniffs_heic():
    header = b"\x00\x00\x00\x18ftypheic" + b"\x00" * 8
    assert sniff_format(header) == "heic"


def test_returns_none_for_unrecognized_format():
    assert sniff_format(b"not-an-image") is None
