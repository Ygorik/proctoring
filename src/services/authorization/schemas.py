from src.base_schemas import BaseResponseSchemas


class AuthorizationSchema(BaseResponseSchemas):
    login: str
    password: str
