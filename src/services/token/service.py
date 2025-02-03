from datetime import timedelta, datetime, timezone

import jwt
from jwt import InvalidTokenError

from src.services.token.exceptions import WrongTokenError
from src.base_schemas import User, Token
from src.config import settings


async def decode_user_token(*, token: str) -> User:
    try:
        user_dict = jwt.decode(
            token,
            settings.TOKEN_SECRET_KEY,
            algorithms=[settings.GENERATE_TOKEN_ALGORITHM],
        )
        return User(**user_dict)
    except InvalidTokenError:
        raise WrongTokenError


class TokenService:
    @staticmethod
    async def create_user_token(
        *, user: User, expires_delta: timedelta | None = None
    ) -> Token:
        to_encode_data = user.dict()

        if expires_delta:
            expire_time = datetime.now(timezone.utc) + expires_delta
        else:
            expire_time = datetime.now(timezone.utc) + timedelta(
                minutes=settings.TOKEN_EXPIRE_MINUTES
            )

        to_encode_data.update({"exp": expire_time})

        return jwt.encode(
            to_encode_data,
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.GENERATE_TOKEN_ALGORITHM,
        )
