import re
from datetime import datetime, timedelta
from typing import List, Optional
from ips_app.domain.models.exception import ValidatorDomainException
from ips_app.domain.models.record import (
    RecordData,
    RecordDataLabel,
    RecordDataMultilateration,
    RecordDataRanging,
)


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


def validate_non_empty_string(value: str, field: str) -> None:
    if not value.strip():
        raise ValidatorDomainException(f"{field} must not be empty.")


def validate_ids_list(ids: List[str], field: str = "ids") -> None:
    if not ids:
        raise ValidatorDomainException(f"'{field}' must not be empty.")
    for item in ids:
        if not item.strip():
            raise ValidatorDomainException(f"Each entry in '{field}' must be a non-empty string.")


def validate_positive_integer(value: int, field: str) -> None:
    if value <= 0:
        raise ValidatorDomainException(f"'{field}' must be greater than 0.")


def validate_optional_non_negative_float(
    value: Optional[float],
    field: str,
) -> None:
    if value is not None and value < 0:
        raise ValidatorDomainException(f"'{field}' must be greater than or equal to 0.")


def validate_uwb_network_value(value: int, field: str) -> None:
    if value < 0 or value > 0xFFFF:
        raise ValidatorDomainException(f"'{field}' must be between 0 and 65535.")


def validate_required_uwb_network_value(value: Optional[int], field: str) -> int:
    if value is None:
        raise ValidatorDomainException(f"'{field}' is required.")
    validate_uwb_network_value(value, field)
    return value


def validate_optional_uwb_network_address(
    pan_id: Optional[int],
    network_address: Optional[int],
) -> None:
    if (pan_id is None) != (network_address is None):
        raise ValidatorDomainException(
            "'pan_id' and 'network_address' must be provided together."
        )
    if pan_id is not None:
        validate_uwb_network_value(pan_id, "pan_id")
    if network_address is not None:
        validate_uwb_network_value(network_address, "network_address")


def validate_user_state_cutoffs(
    away_after: timedelta,
    offline_after: timedelta,
) -> None:
    if away_after.total_seconds() <= 0:
        raise ValidatorDomainException(
            "Away cutoff duration must be greater than 0 seconds."
        )
    if offline_after.total_seconds() <= 0:
        raise ValidatorDomainException(
            "Offline cutoff duration must be greater than 0 seconds."
        )
    if offline_after <= away_after:
        raise ValidatorDomainException(
            "Offline cutoff duration must be greater than away cutoff duration."
        )


def validate_cron_period(period_seconds: int) -> None:
    if period_seconds <= 0:
        raise ValidatorDomainException(
            "USER_STATE_UPDATER_CRON_PERIOD must be greater than 0 seconds."
        )


def validate_record_interval(
    interval_field: str,
    start: datetime,
    end: datetime,
) -> None:
    if interval_field not in ("recorded_at", "created_at"):
        raise ValidatorDomainException(
            "'interval_field' must be either 'recorded_at' or 'created_at'."
        )
    if start > end:
        raise ValidatorDomainException("'start' must be before or equal to 'end'.")


def validate_record_data(
    label: RecordDataLabel,
    data: RecordData,
) -> None:
    if label == RecordDataLabel.RANGING and not isinstance(
        data,
        RecordDataRanging,
    ):
        raise ValidatorDomainException("Ranging records must use ranging record data.")
    if label == RecordDataLabel.MULTILATERATION and not isinstance(
        data,
        RecordDataMultilateration,
    ):
        raise ValidatorDomainException(
            "Multilateration records must use multilateration record data."
        )
