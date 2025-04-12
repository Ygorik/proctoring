from src.config import settings
from src.services.authorization.exceptions import UserNotFoundError
from src.services.role.db_service import RoleDBService
from src.services.role.exceptions import RoleNotFoundError
from src.services.user.db_service import UserDBService
from src.services.user.exceptions import FieldAlreadyUseError
from src.services.user.schemas import (
    RegisterData,
    UserItemForList,
    UserItem,
    PatchUserData,
    UserFilters,
)
from src.utils.cryptographer import Cryptographer
from src.utils.role_checker import (
    check_create_rights,
    check_read_rights,
    check_update_rights,
    check_delete_rights,
)


class UserService:
    def __init__(
        self,
        *,
        user_db_service: UserDBService,
        role_db_service: RoleDBService,
    ) -> None:
        self.user_db_service = user_db_service
        self.role_db_service = role_db_service
        self.cryptographer = Cryptographer(settings.CRYPTO_KEY)

    @check_create_rights
    async def register_user(self, *, register_data: RegisterData) -> None:
        await self.validate_register_data(register_data=register_data)

        register_data.hashed_password = self.cryptographer.encrypt(
            register_data.password
        )

        await self.user_db_service.register_user(register_data=register_data)

    async def validate_register_data(self, *, register_data: RegisterData) -> None:
        if await self.user_db_service.check_login(login=register_data.login):
            raise FieldAlreadyUseError(message="Никнейм уже используется")

        if (
            register_data.role_id
            and await self.role_db_service.get_role_by_id(role_id=register_data.role_id)
            is None
        ):
            raise RoleNotFoundError

    @check_read_rights
    async def get_list_of_users(self, *, filters: UserFilters) -> list[UserItemForList]:
        return await self.user_db_service.get_list_of_users(filters=filters)

    @check_read_rights
    async def get_user_by_id(self, *, user_id: int) -> UserItem:
        return await self.get_user_by_id_if_exist(user_id=user_id)

    @check_update_rights
    async def patch_user_by_id(self, *, user_id: int, user_data: PatchUserData) -> None:
        if user_data.password:
            user_data.hashed_password = self.cryptographer.encrypt(user_data.password)

        if (
            user_data.role_id
            and await self.role_db_service.get_role_by_id(role_id=user_data.role_id)
            is None
        ):
            raise RoleNotFoundError

        await self.user_db_service.patch_user_by_id(
            user_id=user_id, user_data=user_data
        )

    @check_delete_rights
    async def delete_user_by_id(self, *, user_id: int) -> None:
        await self.get_user_by_id_if_exist(user_id=user_id)
        await self.user_db_service.delete_user_by_id(user_id=user_id)

    async def get_user_by_id_if_exist(self, *, user_id: int):
        if user := await self.user_db_service.get_user_by_id(user_id=user_id):
            return user
        raise UserNotFoundError
