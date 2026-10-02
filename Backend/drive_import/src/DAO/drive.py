import os
from functools import lru_cache
from urllib.parse import quote, urlsplit

import boto3
import requests

PUBLIC_MESSAGE = ('We could not access this folder publicly. In Google Drive, open Share, '
                  'set General access to "Anyone with the link", and copy the folder link again. '
                  'The link may also be incorrect or the folder may have been deleted.')


class DriveAccessError(Exception):
    pass


class DriveTransientError(Exception):
    pass


@lru_cache(maxsize=1)
def _api_key():
    return boto3.client("ssm").get_parameter(
        Name=os.environ["DRIVE_API_KEY_PARAMETER"], WithDecryption=True
    )["Parameter"]["Value"]


def _request(file_id=None, resource_key="", params=None, stream=False):
    url = "https://www.googleapis.com/drive/v3/files"
    if file_id:
        url += "/" + quote(file_id, safe="")
    headers = {"X-Goog-Api-Key": _api_key(), "Accept-Encoding": "identity"}
    if resource_key:
        headers["X-Goog-Drive-Resource-Keys"] = resource_key
    try:
        response = requests.get(url, params=params, headers=headers, stream=stream,
                                timeout=(5, 30), allow_redirects=False)
        # Never forward the API key to a redirected host.
        for _ in range(5):
            if not response.is_redirect:
                break
            target = response.headers.get("Location", "")
            parsed = urlsplit(target)
            response.close()
            if (parsed.scheme != "https" or parsed.username or parsed.port not in (None, 443)
                    or not (parsed.hostname or "").endswith((".googleusercontent.com", ".googleapis.com"))):
                raise DriveAccessError("Google returned an unsupported download destination.")
            response = requests.get(target, headers={"Accept-Encoding": "identity"}, stream=stream,
                                    timeout=(5, 30), allow_redirects=False)
    except requests.RequestException:
        raise DriveTransientError("Google Drive could not be reached. Please try again later.") from None
    if response.status_code == 200:
        return response
    try:
        error = response.json().get("error", {})
        reasons = {item.get("reason") for item in error.get("errors", [])}
    except (ValueError, AttributeError):
        reasons = set()
    status = response.status_code
    response.close()
    if status == 429 or status >= 500 or reasons & {"rateLimitExceeded", "userRateLimitExceeded", "downloadQuotaExceeded"}:
        raise DriveTransientError("Google Drive temporarily limited this import. Please try again later.")
    if reasons & {"cannotDownloadFile", "downloadRestrictedForRevision", "fileNotDownloadable"}:
        raise DriveAccessError("Downloads are disabled or unavailable for this file.")
    if status in (403, 404):
        raise DriveAccessError(PUBLIC_MESSAGE)
    raise DriveAccessError("Google Drive could not serve this request. Check the link and try again.")


def folder_metadata(folder_id, resource_key):
    keys = f"{folder_id}/{resource_key}" if resource_key else ""
    with _request(folder_id, keys, {"fields": "id,name,mimeType", "supportsAllDrives": "true"}) as response:
        metadata = response.json()
    if metadata.get("mimeType") != "application/vnd.google-apps.folder":
        raise DriveAccessError("Use a public Google Drive folder link, not a file or ZIP link.")
    return metadata


def list_page(folder_id, resource_key, page_token):
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": "nextPageToken,files(id,name,mimeType,size,resourceKey,capabilities(canDownload))",
        "pageSize": 100, "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
    }
    if page_token:
        params["pageToken"] = page_token
    keys = f"{folder_id}/{resource_key}" if resource_key else ""
    with _request(resource_key=keys, params=params) as response:
        return response.json()


def download(file_id, resource_keys):
    return _request(file_id, resource_keys, {"alt": "media", "supportsAllDrives": "true"}, stream=True)
