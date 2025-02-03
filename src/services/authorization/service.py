from src.base_schemas import Token, User
from src.services.authorization.db_service import AuthorizeDBService
from src.services.authorization.exceptions import (
    UserNotFoundError,
    WrongPasswordError,
)
from src.services.authorization.schemas import AuthorizationSchema
from src.services.token.service import TokenService
from src.utils.cryptographer import Cryptographer


class AuthorizeService:
    def __init__(
        self, *, authorize_db_service: AuthorizeDBService, token_service: TokenService
    ) -> None:
        self.authorize_db_service = authorize_db_service
        self.token_service = token_service
        self.cryptographer = Cryptographer()

    async def authorize_user(self, *, authorization_data: AuthorizationSchema) -> Token:
        user_db = await self.authorize_db_service.get_user_by_login(
            login=authorization_data.login
        )

        if user_db is None:
            raise UserNotFoundError

        if (
            self.cryptographer.decrypt(user_db.hashed_password)
            != authorization_data.password
        ):
            raise WrongPasswordError

        await self.authorize_db_service.insert_authorization(user_id=user_db.id)

        return Token(
            token=await self.token_service.create_user_token(
                user=User(
                    id=str(user_db.id),
                    login=user_db.login,
                )
            )
        )
