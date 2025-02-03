import re

from pydantic import field_validator

from src.base_schemas import BaseResponseSchemas


class RegisterData(BaseResponseSchemas):
    login: str
    password: str
    hashed_password: str | None = None

    @field_validator("password")
    def validate_password(cls, password) -> str:
        password_regex = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#\$%\^&\*()\_\-+=])(?!.*\s).{8,50}"
        if re.match(password_regex, password) is None:
            raise ValueError("Invalid password")
        return password
