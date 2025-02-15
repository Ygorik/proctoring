
from src.config import settings
from src.services.authorization.schemas import Token, User
from src.services.token.service import TokenService
from src.services.registration.db_service import RegisterDBService
from src.services.registration.exceptions import FieldAlreadyUseError
from src.services.registration.schemas import RegisterData
from src.utils.cryptographer import Cryptographer


class RegisterService:
    def __init__(
        self, *, register_db_service: RegisterDBService, token_service: TokenService
    ) -> None:
        self.register_db_service = register_db_service
        self.token_service = token_service
        self.cryptographer = Cryptographer(settings.CRYPTO_KEY)

    async def register_user(self, *, register_data: RegisterData) -> Token:
        await self.validate_register_data(register_data=register_data)

        register_data.hashed_password = self.cryptographer.encrypt(
            register_data.password
        )

        user_db, profile_db = await self.register_db_service.register_user(
            register_data=register_data
        )
        user = User(
            id=str(user_db.id),
            login=user_db.login,
        )

        return Token(token=await self.token_service.create_user_token(user=user))

    async def validate_register_data(self, *, register_data: RegisterData) -> None:
        if await self.register_db_service.check_login(login=register_data.login):
            raise FieldAlreadyUseError(message="Никнейм уже используется")
