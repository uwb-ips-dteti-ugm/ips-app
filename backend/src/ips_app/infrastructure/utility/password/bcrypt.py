import bcrypt

from ips_app.domain.contracts.utility.password import PasswordHasher
from ips_app.domain.models.exception import DomainException, UnexpectedDomainException


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        try:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except DomainException:
            raise
        except Exception as e:
            raise UnexpectedDomainException(str(e)) from e
