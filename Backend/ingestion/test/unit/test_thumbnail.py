import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Converter.thumbnail import make_thumbnail, normalize_to_jpeg


def _make_jpeg_bytes(size=(800, 600)):
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _make_png_bytes(size=(200, 200)):
    image = Image.new("RGB", size, color="blue")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_make_thumbnail_shrinks_to_max_dimension():
    thumbnail_bytes = make_thumbnail(_make_jpeg_bytes(), max_dimension=400)

    image = Image.open(io.BytesIO(thumbnail_bytes))
    assert image.format == "JPEG"
    assert max(image.size) <= 400


def test_normalize_to_jpeg_converts_png_to_jpeg():
    jpeg_bytes = normalize_to_jpeg(_make_png_bytes())

    image = Image.open(io.BytesIO(jpeg_bytes))
    assert image.format == "JPEG"
