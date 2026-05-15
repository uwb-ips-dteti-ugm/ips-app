from ips_app.domain.models.exception import DomainException, UnexpectedDomainException
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driving.cron.user_state_updater import UserStateUpdaterCron


class UserStateUpdaterCronHandler:
    def __init__(
        self,
        service: UserStateUpdaterCron,
        log: GenericLogging,
    ):
        self.service = service
        self.log = log
        self.tag_class = self.__class__.__name__

    async def run_update_user_states(self) -> None:
        tag = f"{self.tag_class}.run_update_user_states"
        try:
            await self.service.update_user_states()
        except DomainException as e:
            await self.log.error(
                tag,
                "User state update rejected",
                {"error": str(e)},
            )
        except Exception as e:
            error = UnexpectedDomainException(str(e))
            await self.log.error(
                tag,
                "User state update failed",
                {"error": str(error)},
            )
