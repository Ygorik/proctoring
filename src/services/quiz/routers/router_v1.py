from fastapi import APIRouter, Depends, Path
from starlette import status

from src.services.authorization.schemas import User
from src.services.quiz.dependencies import quiz_service_dependency
from src.services.quiz.schemas import QuizItemSchema, PatchQuizSchema
from src.services.quiz.service import QuizService
from src.services.token.service import decode_user_token

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def get_list_of_roles(
    quiz_service: QuizService = Depends(quiz_service_dependency),
    user: User = Depends(decode_user_token),
) -> list[QuizItemSchema]:
    return await quiz_service.get_list_of_qiuz(user=user)


@router.get("/{roleId}", status_code=status.HTTP_200_OK)
async def get_role(
    role_id: int = Path(alias="roleId"),
    quiz_service: QuizService = Depends(quiz_service_dependency),
    user: User = Depends(decode_user_token),
) -> QuizItemSchema:
    return await quiz_service.get_quiz_by_id(user=user, role_id=role_id)


@router.patch("/{roleId}", status_code=status.HTTP_200_OK)
async def patch_role(
    role_data: PatchQuizSchema,
    role_id: int = Path(alias="roleId"),
    quiz_service: QuizService = Depends(quiz_service_dependency),
    user: User = Depends(decode_user_token),
) -> None:
    await quiz_service.update_quiz(user=user, role_id=role_id, role_data=role_data)
