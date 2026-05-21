from typing import Awaitable, Callable

from ips_app_old.controllers.cron.handlers.user_state_updater import (
    UserStateUpdaterCronHandler,
)


def create_job(
    handler: UserStateUpdaterCronHandler,
) -> Callable[[], Awaitable[None]]:
    async def update_user_states_job() -> None:
        await handler.run_update_user_states()

    return update_user_states_job
