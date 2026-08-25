import io
import sys
from pathlib import Path

import pillow_heif
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Converter.converter import heic_to_jpeg


def test_heic_to_jpeg_converts_valid_heic():
    source = Image.new("RGB", (8, 8), color=(255, 0, 0))
    heif_file = pillow_heif.from_pillow(source)
    buffer = io.BytesIO()
    heif_file.save(buffer, quality=90)
    heic_bytes = buffer.getvalue()

    jpeg_bytes = heic_to_jpeg(heic_bytes)

    result = Image.open(io.BytesIO(jpeg_bytes))
    assert result.format == "JPEG"
    assert result.size == (8, 8)
