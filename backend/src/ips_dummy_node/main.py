from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import random
import signal
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import quote, urlparse, urlunparse

try:
    from websockets.asyncio.client import connect
    from websockets.exceptions import ConnectionClosed
except ModuleNotFoundError:  # pragma: no cover - runtime dependency guard
    connect = None  # type: ignore[assignment]

    class ConnectionClosed(Exception):  # type: ignore[no-redef]
        pass


COMMAND_RESTART = 1
COMMAND_LISTEN_RANGING = 2
COMMAND_INITIATE_RANGING = 3
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")
DEFAULT_WEBSOCKET_URL = "ws://localhost:8000/nodes/ws"
DEFAULT_RETRY_SECONDS = 3.0


@dataclass(frozen=True)
class DummyNodeConfig:
    device_id: str
    pan_id: int
    x: float
    y: float
    z: float
    noise: float = 0.0


@dataclass(frozen=True)
class DummyNodeAppConfig:
    websocket_url: str
    retry_seconds: float
    nodes: List[DummyNodeConfig]


@dataclass(frozen=True)
class ListenWindow:
    listener_device_id: str
    listener_pan_id: int
    initiator_pan_id: int
    expires_at: float


class RestartRequested(Exception):
    pass


class RangingEnvironment:
    def __init__(self, nodes: Sequence[DummyNodeConfig]):
        self.nodes_by_pan_id = {node.pan_id: node for node in nodes}
        self.listen_windows: Dict[Tuple[int, int], ListenWindow] = {}
        self.lock = asyncio.Lock()

    async def mark_listening(
        self,
        listener: DummyNodeConfig,
        listener_pan_id: int,
        initiator_pan_id: int,
        listen_for_ms: int,
    ) -> None:
        expires_at = time.monotonic() + listen_for_ms / 1000
        async with self.lock:
            self.listen_windows[(listener_pan_id, initiator_pan_id)] = ListenWindow(
                listener_device_id=listener.device_id,
                listener_pan_id=listener_pan_id,
                initiator_pan_id=initiator_pan_id,
                expires_at=expires_at,
            )

    async def range_to_listener(
        self,
        initiator: DummyNodeConfig,
        initiator_pan_id: int,
        listener_pan_id: int,
        wait_for_ms: int,
    ) -> Tuple[Optional[float], bool]:
        listener = self.nodes_by_pan_id.get(listener_pan_id)
        deadline = time.monotonic() + wait_for_ms / 1000

        while True:
            async with self.lock:
                self._prune_expired_listen_windows()
                listen_window = self.listen_windows.get(
                    (listener_pan_id, initiator_pan_id)
                )
                if listen_window is not None:
                    self.listen_windows.pop((listener_pan_id, initiator_pan_id), None)
                    return (
                        self._distance(initiator, listener) if listener else None,
                        True,
                    )

            if time.monotonic() >= deadline:
                return None, False

            await asyncio.sleep(0.01)

    def _prune_expired_listen_windows(self) -> None:
        now = time.monotonic()
        expired_keys = [
            key for key, window in self.listen_windows.items() if window.expires_at < now
        ]
        for key in expired_keys:
            self.listen_windows.pop(key, None)

    def _distance(
        self,
        source: DummyNodeConfig,
        target: DummyNodeConfig,
    ) -> float:
        distance = math.dist((source.x, source.y, source.z), (target.x, target.y, target.z))
        if source.noise > 0:
            distance = random.gauss(distance, source.noise)
        return round(max(distance, 0.0), 4)


class DummyNode:
    def __init__(
        self,
        node: DummyNodeConfig,
        environment: RangingEnvironment,
        websocket_url: str,
        retry_seconds: float,
    ):
        self.node = node
        self.environment = environment
        self.websocket_url = websocket_url
        self.retry_seconds = retry_seconds

    async def run_forever(self, stop_event: asyncio.Event) -> None:
        while not stop_event.is_set():
            try:
                await self._run_connection(stop_event)
            except RestartRequested:
                self._log("Restart requested by server")
            except ConnectionClosed as e:
                self._log(f"Connection closed: {e}")
            except Exception as e:
                self._log(f"Connection rejected or unavailable: {e}")

            if not stop_event.is_set():
                await asyncio.sleep(self.retry_seconds)

    async def _run_connection(self, stop_event: asyncio.Event) -> None:
        uri = build_node_websocket_uri(self.websocket_url, self.node.device_id)
        self._log(f"Connecting to {uri}")
        async with connect(uri) as websocket:
            self._log("Connected")
            while not stop_event.is_set():
                try:
                    raw_message = await asyncio.wait_for(websocket.recv(), timeout=1)
                except asyncio.TimeoutError:
                    continue
                await self._handle_server_message(websocket, raw_message)

    async def _handle_server_message(self, websocket: Any, raw_message: Any) -> None:
        try:
            message = json.loads(raw_message)
        except (TypeError, json.JSONDecodeError):
            self._log(f"Ignored non-JSON message: {raw_message!r}")
            return

        if not isinstance(message, dict):
            self._log(f"Ignored non-object message: {message!r}")
            return

        try:
            command = int(message.get("command", -1))
        except (TypeError, ValueError):
            self._log(f"Ignored command with invalid code: {message!r}")
            return

        payload = message.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}

        if command == COMMAND_RESTART:
            raise RestartRequested()
        if command == COMMAND_LISTEN_RANGING:
            await self._handle_listen_ranging(payload)
            return
        if command == COMMAND_INITIATE_RANGING:
            await self._handle_initiate_ranging(websocket, payload)
            return

        self._log(f"Ignored unknown command: {message!r}")

    async def _handle_listen_ranging(self, payload: Dict[str, Any]) -> None:
        listener_pan_id = int(payload.get("listener_pan_id", -1))
        initiator_pan_id = int(payload.get("initiator_pan_id", -1))
        listen_for_ms = int(payload.get("listen_for_ms", 0))

        if listener_pan_id != self.node.pan_id:
            self._log(
                "Ignored listen command for PAN "
                f"{listener_pan_id}; local PAN is {self.node.pan_id}"
            )
            return

        await self.environment.mark_listening(
            listener=self.node,
            listener_pan_id=listener_pan_id,
            initiator_pan_id=initiator_pan_id,
            listen_for_ms=listen_for_ms,
        )
        self._log(
            "Listening for ranging from PAN "
            f"{initiator_pan_id} for {listen_for_ms} ms"
        )

    async def _handle_initiate_ranging(self, websocket: Any, payload: Dict[str, Any]) -> None:
        initiator_pan_id = int(payload.get("initiator_pan_id", -1))
        listener_pan_id = int(payload.get("listener_pan_id", -1))
        wait_for_ms = int(payload.get("wait_for_ms", 0))

        if initiator_pan_id != self.node.pan_id:
            self._log(
                "Ignored initiate command for PAN "
                f"{initiator_pan_id}; local PAN is {self.node.pan_id}"
            )
            return

        distance, listener_was_ready = await self.environment.range_to_listener(
            initiator=self.node,
            initiator_pan_id=initiator_pan_id,
            listener_pan_id=listener_pan_id,
            wait_for_ms=wait_for_ms,
        )
        await self._send_ranging_record(
            websocket=websocket,
            destination_pan_id=listener_pan_id,
            distance=distance,
        )
        self._log(
            "Reported ranging to PAN "
            f"{listener_pan_id}: {distance if listener_was_ready else 'unreachable'}"
        )

    async def _send_ranging_record(
        self,
        websocket: Any,
        destination_pan_id: int,
        distance: Optional[float],
    ) -> None:
        message = {
            "label": "ranging",
            "data": {
                "source_pan_id": self.node.pan_id,
                "destination_pan_id": destination_pan_id,
                "distance": distance,
            },
        }
        await websocket.send(json.dumps(message))

    def _log(self, message: str) -> None:
        print(f"[{datetime.now(timezone.utc).isoformat()}] {self.node.device_id}: {message}")


def load_config(path: Path) -> DummyNodeAppConfig:
    raw_config = json.loads(path.read_text())
    nodes = [
        parse_node_config(index=index, raw_node=raw_node)
        for index, raw_node in enumerate(raw_config.get("nodes", []), start=1)
    ]
    if not nodes:
        raise ValueError("Dummy node config must contain at least one node.")
    validate_unique_pan_ids(nodes)

    websocket_url = (
        os.getenv("IPS_DUMMY_NODE_WEBSOCKET_URL")
        or raw_config.get("websocket_url")
        or raw_config.get("server_url")
        or DEFAULT_WEBSOCKET_URL
    )
    retry_seconds = float(
        os.getenv("IPS_DUMMY_NODE_RETRY_SECONDS")
        or raw_config.get("retry_seconds")
        or DEFAULT_RETRY_SECONDS
    )
    return DummyNodeAppConfig(
        websocket_url=websocket_url,
        retry_seconds=retry_seconds,
        nodes=nodes,
    )


def validate_unique_pan_ids(nodes: Sequence[DummyNodeConfig]) -> None:
    seen_pan_ids: set[int] = set()
    for node in nodes:
        if node.pan_id in seen_pan_ids:
            raise ValueError(f"Duplicate dummy node pan_id: {node.pan_id}")
        seen_pan_ids.add(node.pan_id)


def parse_node_config(index: int, raw_node: Dict[str, Any]) -> DummyNodeConfig:
    device_id = str(raw_node["device_id"]).strip()
    if not device_id:
        raise ValueError("Dummy node device_id must not be empty.")

    return DummyNodeConfig(
        device_id=device_id,
        pan_id=int(raw_node.get("pan_id", index)),
        x=float(raw_node.get("x", 0.0)),
        y=float(raw_node.get("y", 0.0)),
        z=float(raw_node.get("z", 0.0)),
        noise=max(float(raw_node.get("noise", 0.0)), 0.0),
    )


def build_node_websocket_uri(base_url: str, device_id: str) -> str:
    encoded_device_id = quote(device_id, safe="")
    if "{device_id}" in base_url:
        return base_url.format(device_id=encoded_device_id)

    parsed = urlparse(base_url)
    scheme = parsed.scheme
    if scheme == "http":
        scheme = "ws"
    elif scheme == "https":
        scheme = "wss"
    elif scheme not in {"ws", "wss"}:
        raise ValueError("websocket_url must use ws://, wss://, http://, or https://.")

    path = parsed.path.rstrip("/")
    if not path:
        path = "/nodes/ws"
    path = f"{path}/{encoded_device_id}"

    return urlunparse((scheme, parsed.netloc, path, "", parsed.query, ""))


async def run_dummy_nodes(config: DummyNodeAppConfig) -> None:
    if connect is None:
        raise RuntimeError(
            "Missing 'websockets'. Install backend requirements before running dummy nodes."
        )

    stop_event = asyncio.Event()
    register_stop_handlers(stop_event)

    environment = RangingEnvironment(config.nodes)
    tasks = [
        asyncio.create_task(
            DummyNode(
                node=node,
                environment=environment,
                websocket_url=config.websocket_url,
                retry_seconds=config.retry_seconds,
            ).run_forever(stop_event)
        )
        for node in config.nodes
    ]

    try:
        await stop_event.wait()
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def register_stop_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run IPS dummy UWB nodes.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.getenv("IPS_DUMMY_NODE_CONFIG", DEFAULT_CONFIG_PATH)),
        help="Path to dummy node config JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if connect is None:
        raise SystemExit(
            "Missing 'websockets'. Install backend requirements before running dummy nodes."
        )

    config = load_config(args.config)
    asyncio.run(run_dummy_nodes(config))


if __name__ == "__main__":
    main()
