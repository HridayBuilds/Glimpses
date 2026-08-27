from Manager.build_photos_manifest import handle_build_photos_manifest
from Manager.finalize import handle_finalize
from Manager.index_one_photo import handle_index_one_photo
from Manager.list_attendees import handle_list_attendees
from Manager.match_attendees import handle_match_attendees
from Manager.process_one_photo import handle_process_one_photo
from Manager.stage import handle_stage


def handle_step(step, payload):
    if step == "stage":
        return handle_stage(payload)
    if step == "process_one_photo":
        return handle_process_one_photo(payload)
    if step == "build_photos_manifest":
        return handle_build_photos_manifest(payload)
    if step == "index_one_photo":
        return handle_index_one_photo(payload)
    if step == "finalize":
        return handle_finalize(payload)
    if step == "list_attendees":
        return handle_list_attendees(payload)
    if step == "match_attendees":
        return handle_match_attendees(payload)
    raise ValueError(f"Unknown step: {step}")
