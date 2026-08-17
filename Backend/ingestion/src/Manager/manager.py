from Manager.extract import handle_extract
from Manager.finalize import handle_finalize
from Manager.index_one_photo import handle_index_one_photo
from Manager.match_attendees import handle_match_attendees


def handle_step(step, payload):
    if step == "extract":
        return handle_extract(payload)
    if step == "index_one_photo":
        return handle_index_one_photo(payload)
    if step == "finalize":
        return handle_finalize(payload)
    if step == "match_attendees":
        return handle_match_attendees(payload)
    raise ValueError(f"Unknown step: {step}")
