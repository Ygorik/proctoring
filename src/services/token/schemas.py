from pydantic import EmailStr, Field

from src.base_schemas import BaseResponseSchemas


class RegisterData(BaseResponseSchemas):
    nickname: str
    email: EmailStr
    phone_number: str = Field(pattern=r"7[0-9]{10}")
    password: str = Field(pattern=r"[A-Za-z0-9!@#$%^&()-+=]{8,50}")
