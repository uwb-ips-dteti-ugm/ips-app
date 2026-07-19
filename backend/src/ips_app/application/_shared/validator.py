import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ips_app.domain.models.exception import ValidatorDomainException


def validate_name(value: str) -> None:
    value = value.strip()
    if len(value) < 2 or len(value) > 100:
        raise ValidatorDomainException("Name must be between 2 and 100 characters.")
    if not re.match(r"^[\w\s\-']+$", value, re.UNICODE):
        raise ValidatorDomainException("Name contains invalid characters.")


def validate_resource_name(value: str) -> None:
    value = value.strip()
    if len(value) < 2 or len(value) > 100:
        raise ValidatorDomainException("Name must be between 2 and 100 characters.")
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9 _\-:/]*$", value):
        raise ValidatorDomainException(
            "Name may only contain letters, digits, spaces, underscores, hyphens, colons, and slashes."
        )


def validate_username(value: str) -> None:
    if len(value) < 3 or len(value) > 50:
        raise ValidatorDomainException("Username must be between 3 and 50 characters.")
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._]*[a-zA-Z0-9]$", value):
        raise ValidatorDomainException(
            "Username must start and end with an alphanumeric character."
        )
    if not re.match(r"^[a-zA-Z0-9._]+$", value):
        raise ValidatorDomainException(
            "Username may only contain letters, digits, underscores, and dots."
        )
    if ".." in value:
        raise ValidatorDomainException("Username must not contain consecutive dots.")


def validate_password(value: str) -> None:
    if len(value) < 8 or len(value) > 128:
        raise ValidatorDomainException(
            "Password must be between 8 and 128 characters."
        )


def validate_description(value: str) -> None:
    if len(value) > 2000:
        raise ValidatorDomainException("Description must not exceed 2000 characters.")


def validate_bio(value: str) -> None:
    if len(value) > 2000:
        raise ValidatorDomainException("Bio must not exceed 2000 characters.")


def validate_non_empty_string(value: str, field: str) -> None:
    if not value.strip():
        raise ValidatorDomainException(f"'{field}' must not be empty.")


def validate_ids_list(ids: List[Any], field: str = "ids") -> None:
    if not ids:
        raise ValidatorDomainException(f"'{field}' must not be empty.")
    for item in ids:
        if isinstance(item, str) and not item.strip():
            raise ValidatorDomainException(
                f"Each entry in '{field}' must be a non-empty string."
            )


def validate_preferences(value: Dict[str, Any]) -> None:
    if not isinstance(value, dict):
        raise ValidatorDomainException("Preferences must be a JSON object.")


def validate_positive_integer(value: int, field: str) -> None:
    if value <= 0:
        raise ValidatorDomainException(f"'{field}' must be greater than 0.")


def validate_non_negative_float(value: float, field: str) -> None:
    if value < 0:
        raise ValidatorDomainException(f"'{field}' must be greater than or equal to 0.")


def validate_uwb_value(value: int, field: str) -> None:
    if value < 0 or value > 0xFFFF:
        raise ValidatorDomainException(f"'{field}' must be between 0 and 65535.")


def validate_node_network_assignment(
    network_id: Optional[Any],
    address: Optional[int],
) -> None:
    if (network_id is None) != (address is None):
        raise ValidatorDomainException(
            "'network_id' and 'address' must be provided together."
        )


def validate_record_interval(start: datetime, end: datetime) -> None:
    if start > end:
        raise ValidatorDomainException(
            "The interval start must be before or equal to the interval end."
        )
