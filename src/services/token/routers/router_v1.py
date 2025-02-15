from fastapi import APIRouter, Depends
from starlette import status

from src.services.authorization.schemas import User
from src.services.token.service import decode_user_token

router = APIRouter()


@router.get("/decode", status_code=status.HTTP_200_OK)
async def decode_user_token(user: User = Depends(decode_user_token)) -> User:
    return user
