import re
from urllib.parse import parse_qs, urlsplit


def parse_folder_link(link):
    if not isinstance(link, str):
        raise ValueError("Paste a public Google Drive folder link.")
    try:
        url = urlsplit(link.strip())
        if url.scheme != "https" or url.hostname != "drive.google.com" or url.port not in (None, 443) or url.username:
            raise ValueError
    except ValueError:
        raise ValueError("Paste an HTTPS folder link from drive.google.com.") from None
    match = re.fullmatch(r"/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]+)/?", url.path)
    if not match:
        raise ValueError("Use a Google Drive folder link. Individual files and ZIP links are not supported.")
    key = parse_qs(url.query).get("resourcekey", [""])[0]
    if key and not re.fullmatch(r"[A-Za-z0-9_-]+", key):
        raise ValueError("This folder link has an invalid resource key. Copy the link again from Drive.")
    return match[1], key
