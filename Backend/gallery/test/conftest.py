import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("PHOTOS_TABLE_NAME", "glimpses-photos-test")
os.environ.setdefault("EVENTS_TABLE_NAME", "glimpses-events-test")
os.environ.setdefault("EVENT_ATTENDEES_TABLE_NAME", "glimpses-event-attendees-test")
os.environ.setdefault("PHOTOS_BUCKET", "glimpses-photos-test-bucket")
os.environ.setdefault("CLOUDFRONT_DOMAIN", "d123456.cloudfront.net")
os.environ.setdefault("CLOUDFRONT_KEY_PAIR_ID", "K1234567890ABC")

if "CLOUDFRONT_PRIVATE_KEY" not in os.environ:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    _test_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    os.environ["CLOUDFRONT_PRIVATE_KEY"] = _test_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
