#!/usr/bin/env python3
"""Upload a locally compiled firmware binary to the backend.

Run from the project root:

    python3 firmware/scripts/upload_firmware.py

Reads all settings from firmware/scripts/upload_firmware.config.json (copy it from
upload_firmware.config.example.json and fill in your values). Locates the compiled
binary at firmware/.pio/build/<board_variant>/firmware.bin.
"""

import hashlib
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing dependency: install with `python3 -m pip install -r scripts/requirements.txt`")

SCRIPTS_DIR = Path(__file__).resolve().parent
FIRMWARE_DIR = SCRIPTS_DIR.parent
CONFIG_PATH = SCRIPTS_DIR / "upload_firmware.config.json"
BOARD_VARIANTS = ["esp32dev-8mb", "esp32dev-16mb"]
REQUIRED_FIELDS = ("version", "backend_url", "board_variant", "username", "password")


def read_config() -> dict:
    with open(CONFIG_PATH) as handle:
        config = json.load(handle)

    for field in REQUIRED_FIELDS:
        if not config.get(field):
            raise ValueError(f"'{field}' is missing from {CONFIG_PATH}")

    if config["board_variant"] not in BOARD_VARIANTS:
        raise ValueError(
            f"'board_variant' must be one of {BOARD_VARIANTS}, got '{config['board_variant']}'"
        )

    return config


def sign_in(backend_url: str, username: str, password: str) -> str:
    response = requests.post(
        f"{backend_url}/auth/sign-in",
        json={"username": username, "password": password},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def upload_firmware(
    backend_url: str,
    token: str,
    data: bytes,
    version: str,
    board_variant: str,
    checksum: str,
) -> dict:
    response = requests.post(
        f"{backend_url}/firmware",
        headers={"Authorization": f"Bearer {token}"},
        data={"version": version, "board_variant": board_variant, "checksum": checksum},
        files={"file": ("firmware.bin", data, "application/octet-stream")},
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    return response.json()


def main() -> int:
    try:
        config = read_config()
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"FAILED: could not read {CONFIG_PATH}: {e}")
        return 1

    board_variant = config["board_variant"]
    binary_path = FIRMWARE_DIR / ".pio" / "build" / board_variant / "firmware.bin"
    try:
        with open(binary_path, "rb") as handle:
            data = handle.read()
    except OSError as e:
        print(f"FAILED: could not read {binary_path}: {e}")
        return 1

    size = len(data)
    checksum = hashlib.sha256(data).hexdigest()
    version = config["version"]
    backend_url = config["backend_url"]

    try:
        token = sign_in(backend_url, config["username"], config["password"])
        upload_firmware(backend_url, token, data, version, board_variant, checksum)
    except Exception as e:
        print(f"FAILED: {e}")
        return 1

    print(f"OK: uploaded {version} ({board_variant}, {size} bytes, sha256={checksum})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
