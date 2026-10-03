import json
import uuid

from Converter.drive_link import parse_folder_link
from DAO import dao, drive

FOLDER = "application/vnd.google-apps.folder"
JUNK = frozenset({"thumbs.db", "desktop.ini", ".ds_store", ".nomedia"})


def _authorize(event_id, user_id):
    event = dao.get_item("EVENTS_TABLE_NAME", {"eventID": event_id})
    if not event or event.get("status") != "ACTIVE":
        raise ValueError("Only active events can accept imported photos.")
    if event["organizerID"] == user_id:
        return
    attendee = dao.get_item("EVENT_ATTENDEES_TABLE_NAME", {"eventID": event_id, "userID": user_id})
    if event.get("contributionPolicy") != "ATTENDEES_CAN_ADD" or not attendee or attendee.get("status") != "ATTENDEE":
        raise PermissionError("You do not have permission to add photos to this event.")


def start_import(event_id, user_id, body):
    folder_id, resource_key = parse_folder_link(body.get("folderUrl"))
    try:
        request_id = str(uuid.UUID(body.get("requestId", "")))
    except (ValueError, AttributeError, TypeError):
        raise ValueError("A valid import request ID is required. Reload the page and try again.") from None
    _authorize(event_id, user_id)
    # Retrying the same request cannot start a second import.
    job_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"drive:{event_id}:{user_id}:{request_id}:{folder_id}:{resource_key}"))
    dao.start_execution(job_id, {
        "eventID": event_id, "userID": user_id, "folderID": folder_id,
        "resourceKey": resource_key, "jobId": job_id,
    })
    return {"jobId": job_id}


def _prefix(payload):
    return f"uploads/drive/event/{payload['eventID']}/user/{payload['userID']}/job/{payload['jobId']}/drive"


def initialize(payload):
    started = payload["startedAt"]
    dao.create_job({
        "jobId": payload["jobId"], "eventID": payload["eventID"], "uploaderID": payload["userID"],
        "eventUploaderKey": f"{payload['eventID']}#{payload['userID']}",
        "source": "GOOGLE_DRIVE", "status": "CHECKING", "startedAt": started,
        "succeededCount": 0, "failedCount": 0,
    })
    _authorize(payload["eventID"], payload["userID"])
    metadata = drive.folder_metadata(payload["folderID"], payload["resourceKey"])
    user = dao.get_item("USERS_TABLE_NAME", {"userID": payload["userID"]}) or {}
    dao.update_job(payload["jobId"], {"folderName": metadata.get("name", "Google Drive folder")})
    return {**payload, "page": 0, "pageToken": "", "downloadedCount": 0, "downloadFailedCount": 0,
            "skippedCount": 0, "skippedFolders": 0, "totalCount": 0,
            "uploadedAt": started, "uploaderDisplayName": user.get("displayName"), "uploaderEmail": user.get("email")}


def list_files(payload):
    _authorize(payload["eventID"], payload["userID"])
    response = drive.list_page(payload["folderID"], payload["resourceKey"], payload["pageToken"])
    items, skipped, folders = [], 0, 0
    for file in response.get("files", []):
        name = file.get("name", "")
        if file.get("mimeType") == FOLDER:
            folders += 1
        elif (name.casefold() in JUNK or name.startswith("._") or name.casefold().endswith(".aae")
              or not file.get("mimeType", "").startswith("image/")):
            skipped += 1
        else:
            items.append({**file, **{key: payload[key] for key in (
                "eventID", "userID", "jobId", "uploadedAt", "uploaderDisplayName", "uploaderEmail", "folderID", "resourceKey"
            )}, "fileResourceKey": file.get("resourceKey", "")})
    key = f"{_prefix(payload)}/pages/{payload['page']}/files.json"
    dao.put_json(key, items)
    updated = {**payload, "pageManifestKey": key, "pageToken": response.get("nextPageToken", ""),
               "skippedCount": payload["skippedCount"] + skipped,
               "skippedFolders": payload["skippedFolders"] + folders,
               "totalCount": payload["totalCount"] + len(items)}
    dao.update_job(payload["jobId"], {key: updated[key] for key in ("totalCount", "skippedCount", "skippedFolders")})
    dao.update_job(payload["jobId"], {"status": "DOWNLOADING"})
    return updated


def download_file(payload, context):
    _authorize(payload["eventID"], payload["userID"])
    key = f"{_prefix(payload)}/raw/{payload['id']}"
    result = {key: payload[key] for key in (
        "eventID", "userID", "uploadedAt", "uploaderDisplayName", "uploaderEmail"
    )}
    result.update(filename=payload["name"], rawKey=key)
    if payload.get("capabilities", {}).get("canDownload") is False:
        return {**result, "status": "FAILED", "reason": "Downloads are disabled for this file."}
    keys = []
    for file_id, resource_key in ((payload["folderID"], payload["resourceKey"]), (payload["id"], payload.get("fileResourceKey"))):
        if resource_key:
            keys.append(f"{file_id}/{resource_key}")
    try:
        with drive.download(payload["id"], ",".join(keys)) as response:
            size = payload.get("size", response.headers.get("Content-Length"))
            expected = int(size) if size is not None else None
            dao.upload_chunks(key, response.iter_content(chunk_size=1024 * 1024), context, expected)
    except drive.DriveAccessError as error:
        return {**result, "status": "FAILED", "reason": str(error)}
    return {**result, "status": "SUCCEEDED"}


def collect_page(payload):
    manifest = dao.get_json(payload["downloadResultsKey"])
    staged, errors = [], []
    for status, references in manifest.get("ResultFiles", {}).items():
        if status not in ("SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"):
            continue
        for reference in references:
            for item in dao.get_json(reference["Key"]):
                output = item.get("Output")
                output = json.loads(output) if isinstance(output, str) else output
                if status == "SUCCEEDED" and output and output.get("status") == "SUCCEEDED":
                    staged.append(output)
                else:
                    raw_input = item.get("Input", {})
                    raw_input = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
                    error_name = f"{item.get('Error', '')} {item.get('Cause', '')}"
                    reason = ("Google Drive did not serve this photo after retries. Check the file's sharing and try importing the folder again."
                              if "DriveTransientError" in error_name else "The download could not finish after retries.")
                    errors.append(output or {"filename": raw_input.get("name", "Unknown file"), "status": "FAILED",
                                              "reason": reason})
    page_prefix = f"{_prefix(payload)}/pages/{payload['page']}"
    dao.put_json(page_prefix + "/staged.json", staged)
    dao.put_json(page_prefix + "/failures.json", errors)
    updated = {**payload, "page": payload["page"] + 1,
               "downloadedCount": payload["downloadedCount"] + len(staged),
               "downloadFailedCount": payload["downloadFailedCount"] + len(errors)}
    # Absolute values make a retried collection task safe.
    dao.update_job(payload["jobId"], {key: updated[key] for key in ("downloadedCount", "downloadFailedCount")})
    return updated


def prepare_manifest(payload, context):
    _authorize(payload["eventID"], payload["userID"])
    if not payload["downloadedCount"]:
        message = ("No supported photos were found directly in this folder. Subfolders are not included."
                   if not payload["totalCount"] else "None of the photos could be downloaded. Check public access and download permissions.")
        dao.update_job(payload["jobId"], {"errorMessage": message, "failedCount": payload["downloadFailedCount"]})
        raise ValueError(message)

    def chunks():
        yield b"["
        first = True
        for page in range(payload["page"]):
            for item in dao.get_json(f"{_prefix(payload)}/pages/{page}/staged.json"):
                if not first:
                    yield b","
                yield json.dumps(item).encode()
                first = False
        yield b"]"

    key = f"{_prefix(payload)}/staged-manifest.json"
    dao.upload_chunks(key, chunks(), context, content_type="application/json")
    dao.update_job(payload["jobId"], {"status": "EXTRACTING"})
    return {"eventID": payload["eventID"], "jobId": payload["jobId"], "stagedManifestKey": key}


def combine_results(payload):
    job = dao.get_item("JOBS_TABLE_NAME", {"jobId": payload["jobId"]})
    failed = payload["failedCount"] + int(job.get("downloadFailedCount", 0))
    duplicates = max(0, int(job["totalCount"]) - payload["succeededCount"] - failed)
    dao.update_job(payload["jobId"], {"duplicateCount": duplicates, "failedCount": failed,
                                      "succeededCount": payload["succeededCount"]})
    return {**payload, "failedCount": failed, "duplicateCount": duplicates}


def fail(payload):
    job = dao.get_item("JOBS_TABLE_NAME", {"jobId": payload["jobId"]}) or {}
    message = job.get("errorMessage") or "The import could not finish. Some photos may already have been added. Please try again."
    failure = payload.get("driveError", {})
    if failure.get("Error") in ("DriveAccessError", "DriveTransientError", "ValueError", "PermissionError"):
        try:
            message = json.loads(failure["Cause"])["errorMessage"]
        except (KeyError, ValueError, TypeError):
            pass
    dao.update_job(payload["jobId"], {"status": "FAILED", "errorMessage": message,
                                      "failedCount": int(payload.get("failedCount", max(job.get("failedCount", 0), job.get("downloadFailedCount", 0))))})
    return {"jobId": payload["jobId"], "status": "FAILED"}


def handle_step(payload, context):
    step = payload["step"]
    if step == "download":
        return download_file(payload, context)
    if step == "prepare_manifest":
        return prepare_manifest(payload, context)
    actions = {"initialize": initialize, "list": list_files, "collect": collect_page,
               "combine": combine_results, "fail": fail}
    return actions[step](payload)
