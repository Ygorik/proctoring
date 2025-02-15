from typing import Callable

from src.services.authorization.schemas import User
from src.services.role.exceptions import (
    UserCanNotReadError,
    UserCanNotCreateError,
    UserCanNotUpdateError,
    UserCanNotDeleteError,
)


def check_read_rights(coroutine: Callable) -> Callable:
    async def wrapper(*args, user: User, **kwargs):
        if user.role is None or not user.role.rights_read:
            raise UserCanNotReadError

        return await coroutine(*args, user=user, **kwargs)

    return wrapper


def check_create_rights(coroutine: Callable) -> Callable:
    async def wrapper(*args, user: User, **kwargs):
        if user.role is None or not user.role.rights_create:
            raise UserCanNotCreateError

        return await coroutine(*args, user=user, **kwargs)

    return wrapper


def check_update_rights(coroutine: Callable) -> Callable:
    async def wrapper(*args, user: User, **kwargs):
        if user.role is None or not user.role.rights_update:
            raise UserCanNotUpdateError

        return await coroutine(*args, user=user, **kwargs)

    return wrapper


def check_delete_rights(coroutine: Callable) -> Callable:
    async def wrapper(*args, user: User, **kwargs):
        if user.role is None or not user.role.rights_delete:
            raise UserCanNotDeleteError

        return await coroutine(*args, user=user, **kwargs)

    return wrapper
