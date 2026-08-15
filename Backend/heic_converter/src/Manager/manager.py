from Converter.converter import heic_to_jpeg
from DAO.dao import get_object, put_object


def convert_and_store(bucket, key):
    heic_bytes = get_object(bucket, key)
    jpeg_bytes = heic_to_jpeg(heic_bytes)
    new_key = key.rsplit(".", 1)[0] + ".jpg"
    put_object(bucket, new_key, jpeg_bytes)
    return new_key
