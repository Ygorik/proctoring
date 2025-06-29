from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseBackendError(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        message: str | None = None,
        data: list | None = None,
        headers: dict | None = None
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={"message": message, "data": data},
            headers=headers,
        )


class BaseResponseSchemas(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, alias_generator=to_camel, from_attributes=True
    )
