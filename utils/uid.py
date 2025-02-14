

import uuid

def uid(phone):
    suffix = phone[-4:]
    short_uuid = uuid.uuid4().hex[:16].upper()
    return suffix + short_uuid
