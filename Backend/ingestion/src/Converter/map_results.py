import json


def parse_result_manifest(manifest_bytes):
    manifest = json.loads(manifest_bytes)
    result_files = manifest.get("ResultFiles", {})
    return result_files.get("SUCCEEDED", []), result_files.get("FAILED", [])


def parse_result_file(result_bytes):
    return [json.loads(item["Output"]) for item in json.loads(result_bytes)]


def count_result_items(result_bytes):
    return len(json.loads(result_bytes))
