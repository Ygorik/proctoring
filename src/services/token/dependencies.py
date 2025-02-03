from src.services.token.service import TokenService


async def token_service_dependency() -> TokenService:
    return TokenService()
