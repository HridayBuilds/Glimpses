import io

import pillow_heif
from PIL import Image


def heic_to_jpeg(heic_bytes: bytes) -> bytes:
    heif_file = pillow_heif.read_heif(heic_bytes)
    image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    return buffer.getvalue()
