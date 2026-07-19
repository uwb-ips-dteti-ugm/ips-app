import asyncio
from typing import Awaitable, Callable

from ips_app.presentation.task.handlers.ranging_scheduler import RangingSchedulerHandler


def create_runner(
    handler: RangingSchedulerHandler,
    listen_timeout_uus: int,
    initiate_timeout_uus: int,
    listen_to_initiate_delay_ms: int,
    pair_delay_ms: int,
    idle_delay_ms: int,
) -> Callable[[], Awaitable[None]]:
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
