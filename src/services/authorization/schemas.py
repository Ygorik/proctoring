from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from src.services.role.schemas import RoleItemSchema

from src.base_schemas import BaseResponseSchemas


class AuthorizationSchema(BaseResponseSchemas):
    login: str
    password: str


class UserFromDB(BaseResponseSchemas):
    id: UUID
    email: EmailStr
    phone_number: str | None
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    role: RoleItemSchema


class User(BaseResponseSchemas):
    id: str
    login: str
    role: RoleItemSchema | None


class Token(BaseResponseSchemas):
    token: str
