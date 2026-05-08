import re
from typing import List
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
        raise ValidatorDomainException("Username must start and end with an alphanumeric character.")
    if not re.match(r"^[a-zA-Z0-9._]+$", value):
        raise ValidatorDomainException("Username may only contain letters, digits, underscores, and dots.")
    if ".." in value:
        raise ValidatorDomainException("Username must not contain consecutive dots.")


def validate_password(value: str) -> None:
    if len(value) < 8 or len(value) > 128:
        raise ValidatorDomainException("Password must be between 8 and 128 characters.")


def validate_description(value: str) -> None:
    if len(value) > 500:
        raise ValidatorDomainException("Description must not exceed 500 characters.")


def validate_bio(value: str) -> None:
    if len(value) > 500:
        raise ValidatorDomainException("Bio must not exceed 500 characters.")


def validate_ids_list(ids: List[str], field: str = "ids") -> None:
    if not ids:
        raise ValidatorDomainException(f"'{field}' must not be empty.")
    for item in ids:
        if not item.strip():
            raise ValidatorDomainException(f"Each entry in '{field}' must be a non-empty string.")
