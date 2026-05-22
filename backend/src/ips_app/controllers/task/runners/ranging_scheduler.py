import asyncio
from typing import Any, Callable, Coroutine

from ips_app.controllers.task.handlers.ranging_scheduler import (
    RangingSchedulerTaskHandler,
)
from ips_app.utils.validator import validate_positive_integer


def create_runner(
    handler: RangingSchedulerTaskHandler,
    listen_timeout_uus: int,
    initiate_timeout_uus: int,
    listen_to_initiate_delay_ms: int,
    pair_delay_ms: int,
    idle_delay_ms: int,
) -> Callable[[], Coroutine[Any, Any, None]]:
    validate_positive_integer(listen_timeout_uus, "listen_timeout_uus")
    validate_positive_integer(initiate_timeout_uus, "initiate_timeout_uus")
    validate_positive_integer(
        listen_to_initiate_delay_ms,
        "listen_to_initiate_delay_ms",
    )
    validate_positive_integer(pair_delay_ms, "pair_delay_ms")
    validate_positive_integer(idle_delay_ms, "idle_delay_ms")

    async def ranging_scheduler_runner() -> None:
        await handler.refresh_registered_nodes()

        while True:
            cycle_done = await handler.run_next_ranging(
                listen_timeout_uus=listen_timeout_uus,
                initiate_timeout_uus=initiate_timeout_uus,
                listen_to_initiate_delay_ms=listen_to_initiate_delay_ms,
            )
            if cycle_done is None:
                await asyncio.sleep(idle_delay_ms / 1000)
                continue
            if cycle_done:
                await handler.refresh_registered_nodes()

            await asyncio.sleep(pair_delay_ms / 1000)

    return ranging_scheduler_runner
