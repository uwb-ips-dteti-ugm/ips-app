from datetime import datetime, timedelta, timezone

from ips_app.domain.models.exception import (
    DomainException,
    UnexpectedDomainException,
)
from ips_app.domain.ports.driven.logging.generic import GenericLogging
from ips_app.domain.ports.driven.repository.user import UserRepository
from ips_app.domain.ports.driving.cron.user_state_updater import UserStateUpdaterCron
from ips_app.utils.validator import validate_user_state_cutoffs


class BaseUserStateUpdaterCron(UserStateUpdaterCron):
    def __init__(
        self,
        repo_user: UserRepository,
        log: GenericLogging,
        away_after_seconds: int,
        offline_after_seconds: int,
    ):
        away_after = timedelta(seconds=away_after_seconds)
        offline_after = timedelta(seconds=offline_after_seconds)
        validate_user_state_cutoffs(away_after, offline_after)

        self.repo_user = repo_user
        self.log = log
        self.away_after = away_after
        self.offline_after = offline_after
        self.tag_class = "BaseUserStateUpdaterCron"

    async def update_user_states(self) -> None:
        tag = f"{self.tag_class}.update_user_states"
        try:
            now = datetime.now(timezone.utc)
            away_cutoff = now - self.away_after
            offline_cutoff = now - self.offline_after

            (
                away_count,
                offline_count,
            ) = await self.repo_user.update_users_state_with_cutoffs(
                away_cutoff=away_cutoff,
                offline_cutoff=offline_cutoff,
            )
            await self.log.info(
                tag,
                "Successfully updated user states",
                {
                    "away_count": away_count,
                    "offline_count": offline_count,
                },
            )
        except DomainException:
            raise
        except Exception as e:
            await self.log.error(
                tag,
                "Failed to update user states",
                {
                    "error": str(e),
                    "away_after_seconds": self.away_after.total_seconds(),
                    "offline_after_seconds": self.offline_after.total_seconds(),
                },
            )
            raise UnexpectedDomainException(str(e)) from e
