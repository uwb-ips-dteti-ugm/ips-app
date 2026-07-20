#!/usr/bin/env python3
"""Check whether a node's `/nodes/ws/{device_id}` connection is accepted or rejected by the backend."""

import asyncio
import sys

import websockets


async def check(url: str, wait_seconds: float) -> int:
    try:
        async with websockets.connect(url, open_timeout=5) as ws:
            print(f"OK: handshake accepted ({url})")
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=wait_seconds)
                print(f"RECV: {message}")
            except asyncio.TimeoutError:
                print(f"OK: connection open, no message within {wait_seconds}s (normal if idle)")
            return 0
    except websockets.exceptions.InvalidStatus as e:
        print(f"REJECTED: HTTP {e.response.status_code} during handshake")
        print("hint: node likely does not exist yet, is not 'approved', or has no network/address assigned")
        return 1
    except websockets.exceptions.ConnectionClosedError as e:
        code = e.rcvd.code if e.rcvd else "?"
        reason = e.rcvd.reason if e.rcvd else "?"
        print(f"REJECTED: closed with code={code} reason={reason}")
        return 1
    except (OSError, asyncio.TimeoutError) as e:
        print(f"UNREACHABLE: {e}")
        return 2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: check_node_ws.py ws://host:port/nodes/ws/<device_id> [wait_seconds]")
        sys.exit(2)
    url = sys.argv[1]
    wait_seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
    sys.exit(asyncio.run(check(url, wait_seconds)))
