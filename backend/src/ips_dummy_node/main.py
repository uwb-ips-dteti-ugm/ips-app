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

WebSocketConnectionClosed: type[BaseException]

try:
    from websockets.asyncio.client import connect
    from websockets.exceptions import ConnectionClosed as _WebSocketConnectionClosed
except ModuleNotFoundError:  # pragma: no cover - runtime dependency guard
    connect = None  # type: ignore[assignment]
    WebSocketConnectionClosed = Exception
else:
    WebSocketConnectionClosed = _WebSocketConnectionClosed


COMMAND_RESTART = 1
COMMAND_LISTEN_RANGING = 2
COMMAND_INITIATE_RANGING = 3
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")
DEFAULT_WEBSOCKET_URL = "ws://localhost:8000/nodes/ws"
DEFAULT_RETRY_SECONDS = 3.0
MAX_UWB_VALUE = 0xFFFF


@dataclass(frozen=True)
class DummyNodeConfig:
    device_id: str
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
    pan_id: int
    listener_address: int
    initiator_address: int
    expires_at: float


class RestartRequested(Exception):
    pass


class RangingEnvironment:
    def __init__(self):
        self.nodes_by_network_address: Dict[Tuple[int, int], DummyNodeConfig] = {}
        self.listen_windows: Dict[Tuple[int, int, int], ListenWindow] = {}
        self.lock = asyncio.Lock()

    async def mark_listening(
        self,
        listener: DummyNodeConfig,
        pan_id: int,
        listener_address: int,
        initiator_address: int,
        timeout_uus: int,
    ) -> None:
        expires_at = time.monotonic() + timeout_uus_to_seconds(timeout_uus)
        async with self.lock:
            self.nodes_by_network_address[(pan_id, listener_address)] = listener
            self.listen_windows[
                (pan_id, listener_address, initiator_address)
            ] = ListenWindow(
                listener_device_id=listener.device_id,
                pan_id=pan_id,
                listener_address=listener_address,
                initiator_address=initiator_address,
                expires_at=expires_at,
            )

    async def range_to_listener(
        self,
        initiator: DummyNodeConfig,
        pan_id: int,
        initiator_address: int,
        listener_address: int,
        timeout_uus: int,
    ) -> Tuple[Optional[float], bool]:
        deadline = time.monotonic() + timeout_uus_to_seconds(timeout_uus)

        while True:
            async with self.lock:
                self.nodes_by_network_address[(pan_id, initiator_address)] = initiator
                self._prune_expired_listen_windows()
                listen_window = self.listen_windows.get(
                    (pan_id, listener_address, initiator_address)
                )
                if listen_window is not None:
                    self.listen_windows.pop(
                        (pan_id, listener_address, initiator_address),
                        None,
                    )
                    listener = self.nodes_by_network_address.get(
                        (pan_id, listener_address)
                    )
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
            except WebSocketConnectionClosed as e:
                self._log(f"Connection closed: {e}")
            except Exception as e:
                self._log(f"Connection rejected or unavailable: {e}")

            if not stop_event.is_set():
                await asyncio.sleep(self.retry_seconds)

    async def _run_connection(self, stop_event: asyncio.Event) -> None:
        uri = build_node_websocket_uri(self.websocket_url, self.node.device_id)
        self._log(f"Connecting to {uri}")
        websocket_connect = connect
        if websocket_connect is None:
            raise RuntimeError(
                "Missing 'websockets'. Install backend requirements before running dummy nodes."
            )

        async with websocket_connect(uri) as websocket:
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
        command = self._read_ranging_command(payload)
        if command is None:
            return
        pan_id, listener_address, initiator_address, timeout_uus = command

        await self.environment.mark_listening(
            listener=self.node,
            pan_id=pan_id,
            listener_address=listener_address,
            initiator_address=initiator_address,
            timeout_uus=timeout_uus,
        )
        self._log(
            "Listening for ranging from "
            f"PAN {pan_id} address {initiator_address} for {timeout_uus} uus"
        )

    async def _handle_initiate_ranging(self, websocket: Any, payload: Dict[str, Any]) -> None:
        command = self._read_ranging_command(payload)
        if command is None:
            return
        pan_id, listener_address, initiator_address, timeout_uus = command

        distance, listener_was_ready = await self.environment.range_to_listener(
            initiator=self.node,
            pan_id=pan_id,
            initiator_address=initiator_address,
            listener_address=listener_address,
            timeout_uus=timeout_uus,
        )
        if listener_was_ready and distance is not None:
            await self._send_ranging_record(
                websocket=websocket,
                pan_id=pan_id,
                source_address=initiator_address,
                destination_address=listener_address,
                distance=distance,
            )
        else:
            await self._send_error(
                websocket=websocket,
                pan_id=pan_id,
                source_address=initiator_address,
                destination_address=listener_address,
                message="Dummy listener did not answer before ranging timeout.",
            )
        self._log(
            "Reported ranging to "
            f"PAN {pan_id} address {listener_address}: "
            f"{distance if listener_was_ready and distance is not None else 'unreachable'}"
        )

    async def _send_ranging_record(
        self,
        websocket: Any,
        pan_id: int,
        source_address: int,
        destination_address: int,
        distance: float,
    ) -> None:
        message = {
            "label": "ranging",
            "data": {
                "pan_id": pan_id,
                "source_address": source_address,
                "destination_address": destination_address,
                "distance": distance,
            },
        }
        await websocket.send(json.dumps(message))

    async def _send_error(
        self,
        websocket: Any,
        pan_id: int,
        source_address: int,
        destination_address: int,
        message: str,
    ) -> None:
        await websocket.send(
            json.dumps(
                {
                    "label": "error",
                    "data": {
                        "pan_id": pan_id,
                        "source_address": source_address,
                        "destination_address": destination_address,
                        "message": message,
                    },
                }
            )
        )

    def _read_ranging_command(
        self,
        payload: Dict[str, Any],
    ) -> Optional[Tuple[int, int, int, int]]:
        try:
            pan_id = parse_uwb_value(payload["pan_id"], "pan_id")
            listener_address = parse_uwb_value(
                payload["listener_address"],
                "listener_address",
            )
            initiator_address = parse_uwb_value(
                payload["initiator_address"],
                "initiator_address",
            )
            timeout_uus = parse_positive_integer(
                payload["timeout_uus"],
                "timeout_uus",
            )
        except (KeyError, TypeError, ValueError) as e:
            self._log(f"Ignored invalid ranging command payload: {e}")
            return None

        return pan_id, listener_address, initiator_address, timeout_uus

    def _log(self, message: str) -> None:
        print(f"[{datetime.now(timezone.utc).isoformat()}] {self.node.device_id}: {message}")


def load_config(path: Path) -> DummyNodeAppConfig:
    raw_config = json.loads(path.read_text())
    nodes = [
        parse_node_config(raw_node=raw_node)
        for raw_node in raw_config.get("nodes", [])
    ]
    if not nodes:
        raise ValueError("Dummy node config must contain at least one node.")
    validate_unique_nodes(nodes)

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


def validate_unique_nodes(nodes: Sequence[DummyNodeConfig]) -> None:
    seen_device_ids: set[str] = set()
    for node in nodes:
        if node.device_id in seen_device_ids:
            raise ValueError(f"Duplicate dummy node device_id: {node.device_id}")
        seen_device_ids.add(node.device_id)


def parse_node_config(raw_node: Dict[str, Any]) -> DummyNodeConfig:
    device_id = str(raw_node["device_id"]).strip()
    if not device_id:
        raise ValueError("Dummy node device_id must not be empty.")

    return DummyNodeConfig(
        device_id=device_id,
        x=float(raw_node.get("x", 0.0)),
        y=float(raw_node.get("y", 0.0)),
        z=float(raw_node.get("z", 0.0)),
        noise=max(float(raw_node.get("noise", 0.0)), 0.0),
    )


def parse_uwb_value(raw_value: Any, name: str) -> int:
    value = parse_integer(raw_value, name)
    if value < 0 or value > MAX_UWB_VALUE:
        raise ValueError(f"{name} must be an integer from 0 to {MAX_UWB_VALUE}.")
    return value


def parse_positive_integer(raw_value: Any, name: str) -> int:
    value = parse_integer(raw_value, name)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value


def parse_integer(raw_value: Any, name: str) -> int:
    try:
        if isinstance(raw_value, str):
            return int(raw_value, base=0)
        return int(raw_value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"{name} must be an integer.") from e


def timeout_uus_to_seconds(timeout_uus: int) -> float:
    return timeout_uus / 1_000_000


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

    environment = RangingEnvironment()
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
