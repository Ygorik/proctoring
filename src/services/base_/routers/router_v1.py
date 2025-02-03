from fastapi import APIRouter, Depends
from starlette import status

from src.services.base_.dependencies import service_dependency
from src.services.base_.service import Service


router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def do_it(
    service: Service = Depends(service_dependency),
):
    service.__repr__()
