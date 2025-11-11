from fastapi import Header
from cryptography.fernet import InvalidToken

from src.config import settings
from src.services.token.exceptions import WrongTokenError
from src.utils.cryptographer import Cryptographer

cryptographer = Cryptographer(settings.MOODLE_SECRET_KEY)

async def check_moodle_token(token: str = Header()) -> None:
    if not token:
        raise WrongTokenError

    try:
        if cryptographer.decrypt(token) != settings.MOODLE_SECRET:
            raise WrongTokenError
    except (InvalidToken, Exception):
        raise WrongTokenError
