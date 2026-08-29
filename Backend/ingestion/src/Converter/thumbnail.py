import io

from PIL import Image, ImageOps

THUMBNAIL_MAX_DIMENSION = 400
JPEG_QUALITY = 85


def make_thumbnail(jpeg_bytes, max_dimension=THUMBNAIL_MAX_DIMENSION):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(jpeg_bytes)))
    image.thumbnail((max_dimension, max_dimension))
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY)
    return buffer.getvalue()


def normalize_to_jpeg(image_bytes):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(image_bytes)))
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY)
    return buffer.getvalue()
