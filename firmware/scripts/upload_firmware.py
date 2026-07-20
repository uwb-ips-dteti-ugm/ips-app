#!/usr/bin/env python3
"""Upload a locally compiled firmware binary and its metadata to the backend."""

import argparse
import hashlib
import sys

try:
    import requests
except ImportError:
    raise SystemExit("Missing dependency: install with `python3 -m pip install -r scripts/requirements.txt`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="path to the compiled .bin")
    parser.add_argument("--version", required=True, help="firmware version, e.g. 1.2.0")
    parser.add_argument(
        "--board-variant",
        required=True,
        choices=["esp32dev-8mb", "esp32dev-16mb"],
        help="PlatformIO environment the binary was built for",
    )
    parser.add_argument("--backend-url", required=True, help="e.g. http://localhost:8000")
    parser.add_argument("--token", help="bearer access token (skips sign-in)")
    parser.add_argument("--username", help="admin username, used if --token is not given")
    parser.add_argument("--password", help="admin password, used if --token is not given")
    return parser.parse_args()


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
    args = parse_args()

    if not args.token and not (args.username and args.password):
        print("FAILED: provide either --token or both --username and --password")
        return 2

    try:
        with open(args.file, "rb") as handle:
            data = handle.read()
    except OSError as e:
        print(f"FAILED: could not read {args.file}: {e}")
        return 1

    size = len(data)
    checksum = hashlib.sha256(data).hexdigest()

    try:
        token = args.token or sign_in(args.backend_url, args.username, args.password)
        upload_firmware(args.backend_url, token, data, args.version, args.board_variant, checksum)
    except Exception as e:
        print(f"FAILED: {e}")
        return 1

    print(
        f"OK: uploaded {args.version} ({args.board_variant}, {size} bytes, sha256={checksum})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
