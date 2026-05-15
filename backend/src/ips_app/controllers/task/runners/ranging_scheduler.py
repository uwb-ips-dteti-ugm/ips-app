import asyncio
from typing import Awaitable, Callable

from ips_app.controllers.task.handlers.ranging_scheduler import (
    RangingSchedulerTaskHandler,
)
from ips_app.utils.validator import validate_positive_integer


WAIT_FOR_NODE_PAIR_SLEEP_MS = 3000


def create_runner(
    handler: RangingSchedulerTaskHandler,
    sleep_ms: int,
    listen_for_ms: int,
    wait_for_ms: int,
) -> Callable[[], Awaitable[None]]:
    validate_positive_integer(sleep_ms, "sleep_ms")
    validate_positive_integer(
        listen_for_ms,
        "listen_for_ms",
    )
    validate_positive_integer(wait_for_ms, "wait_for_ms")

    async def ranging_scheduler_runner() -> None:
        await handler.refresh_registered_nodes()

        while True:
            cycle_done = await handler.run_next_ranging(
                listen_for_ms=listen_for_ms,
                wait_for_ms=wait_for_ms,
            )
            if cycle_done is None:
                await asyncio.sleep(WAIT_FOR_NODE_PAIR_SLEEP_MS / 1000)
                continue
            if cycle_done:
                await handler.refresh_registered_nodes()

            await asyncio.sleep(sleep_ms / 1000)

    return ranging_scheduler_runner
