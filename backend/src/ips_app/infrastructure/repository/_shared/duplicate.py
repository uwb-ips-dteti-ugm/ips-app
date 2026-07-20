from typing import List

from pymongo.errors import DuplicateKeyError


def duplicate_key_fields(error: DuplicateKeyError) -> List[str]:
    key_pattern = error.details.get("keyPattern", {}) if error.details else {}
    return list(key_pattern.keys())
