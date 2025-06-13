import re
from uuid import UUID

from fastapi import Query
from pydantic import field_validator, Field

from src.base_schemas import BaseResponseSchemas
from src.services.role.schemas import RoleItemSchema


class RegisterData(BaseResponseSchemas):
    full_name: str
    login: str
    password: str
    role_id: int | None = None
    hashed_password: str | None = None

    @field_validator("password")
    def validate_password(cls, password) -> str:
        password_regex = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#\$%\^&\*()\_\-+=])(?!.*\s).{8,50}"
        if re.match(password_regex, password) is None:
            raise ValueError("Invalid password")
        return password


class UserItemForList(BaseResponseSchemas):
    id: int
    full_name: str
    login: str
    role_name: str


class UserItem(UserItemForList):
    role: RoleItemSchema


class PatchUserData(BaseResponseSchemas):
    full_name: str | None = None
    login: str | None = None
    password: str | None = None
    role_id: int | None = None
    hashed_password: str | None = None

    @field_validator("password")
    def validate_password(cls, password) -> str:
        password_regex = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#\$%\^&\*()\_\-+=])(?!.*\s).{8,50}"
        if password and re.match(password_regex, password) is None:
            raise ValueError("Invalid password")
        return password


class UserFilters:
    def __init__(
        self,
        subject_id: int | None = Query(default=None, alias="subjectId"),
        role_id: int | None = Query(default=None, alias="roleId"),
    ):
        self.subject_id = subject_id
        self.role_id = role_id
