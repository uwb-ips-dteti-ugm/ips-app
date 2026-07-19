import asyncio
from typing import Awaitable, Callable

from ips_app.domain.usecases.ranging_scheduler_config import RangingSchedulerConfigUsecase
from ips_app.presentation.task.handlers.ranging_scheduler import RangingSchedulerHandler


def create_runner(
    handler: RangingSchedulerHandler,
    config_usecase: RangingSchedulerConfigUsecase,
) -> Callable[[], Awaitable[None]]:
    async def ranging_scheduler_runner() -> None:
        await handler.refresh_registered_nodes()
        while True:
            config = await config_usecase.get_config()
            cycle_done = await handler.run_next_ranging(
                listen_timeout_uus=config.listen_timeout_uus,
                initiate_timeout_uus=config.initiate_timeout_uus,
                listen_to_initiate_delay_ms=config.listen_to_initiate_delay_ms,
            )
            if cycle_done is None:
                await asyncio.sleep(config.idle_delay_ms / 1000)
                continue
            if cycle_done:
                await handler.refresh_registered_nodes()
            await asyncio.sleep(config.pair_delay_ms / 1000)

    return ranging_scheduler_runner
