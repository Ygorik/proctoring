import numpy as np
from fastapi import UploadFile

from src.services.authorization.exceptions import UserNotFoundError
from src.services.mediapipe.start_proctoring import handle_proctoring
from src.services.proctoring.db_service import ProctoringDBService
from src.services.proctoring.exceptions import ProctoringNotFoundError, NotImageError
from src.services.proctoring.schemas import (
    ProctoringItemSchema,
    CreateProctoringSchema,
    PatchProctoringSchema,
    CreateProctoringTypeSchema,
    ProctoringTypeItemSchema,
    UpdateProctoringTypeSchema,
    ProctoringFilters, ProctoringDataSchema,
)
from src.services.proctoring_result.db_service import ProctoringResultDBService
from src.services.subject.db_service import SubjectDBService
from src.services.subject.exceptions import SubjectNotFoundError
from src.services.subject.schemas import SubjectSchema
from src.services.user.db_service import UserDBService
from src.services.user.schemas import UserItem

from src.utils.role_checker import (
    check_read_rights,
    check_delete_rights,
    check_update_rights,
    check_create_rights,
)


class ProctoringService:
    def __init__(
        self,
        *,
        proctoring_db_service: ProctoringDBService,
        user_db_service: UserDBService,
        subject_db_service: SubjectDBService,
        proctoring_result_db_service: ProctoringResultDBService,
    ) -> None:
        self.proctoring_db_service = proctoring_db_service
        self.user_db_service = user_db_service
        self.subject_db_service = subject_db_service
        self.proctoring_result_db_service = proctoring_result_db_service

    @check_create_rights
    async def create_proctoring_type(
            self, *, proctoring_type_data: CreateProctoringTypeSchema
    ):
        await self.proctoring_db_service.insert_proctoring_type(
            proctoring_type_data=proctoring_type_data
        )

    @check_read_rights
    async def get_list_of_proctoring_types(self) -> list[ProctoringTypeItemSchema]:
        return await self.proctoring_db_service.get_list_of_proctoring_types()

    @check_read_rights
    async def get_proctoring_type_by_id(
            self, *, proctoring_type_id: int
    ) -> ProctoringTypeItemSchema:
        return await self.get_proctoring_type_by_id_if_exist(
            proctoring_type_id=proctoring_type_id
        )

    @check_update_rights
    async def update_proctoring_type(
            self,
            *,
            proctoring_type_id: int,
            proctoring_type_data: UpdateProctoringTypeSchema,
    ) -> None:
        await self.get_proctoring_type_by_id_if_exist(
            proctoring_type_id=proctoring_type_id
        )

        await self.proctoring_db_service.update_proctoring_type(
            proctoring_type_id=proctoring_type_id,
            proctoring_type_data=proctoring_type_data,
        )

    @check_delete_rights
    async def delete_proctoring_type(self, *, proctoring_type_id: int) -> None:
        await self.get_proctoring_type_by_id_if_exist(
            proctoring_type_id=proctoring_type_id
        )

        await self.proctoring_db_service.delete_proctoring_type_by_id(
            proctoring_type_id=proctoring_type_id
        )

    @check_create_rights
    async def create_proctoring(
            self, *, proctoring_data: CreateProctoringSchema
    ) -> None:
        await self.get_proctoring_type_by_id_if_exist(
            proctoring_type_id=proctoring_data.type_id
        )
        await self.get_subject_by_id_if_exist(subject_id=proctoring_data.subject_id)
        await self.get_user_by_id_if_exist(user_id=proctoring_data.user_id)

        await self.proctoring_db_service.create_proctoring(
            proctoring_data=proctoring_data
        )

    @check_read_rights
    async def get_list_of_proctoring(
            self, *, filters: ProctoringFilters | None
    ) -> list[ProctoringItemSchema]:
        return [
            ProctoringItemSchema(
                proctoring_name=orm.proctoring_type.name,
                user_name=orm.user.full_name,
                subject_name=orm.subject.name,
                result_id=orm.result_id
            )
            for orm in await self.proctoring_db_service.get_list_of_proctoring(
                filters=filters
            )
        ]

    @check_read_rights
    async def get_proctoring_by_id(self, *, proctoring_id: int) -> ProctoringItemSchema:
        return await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)

    @check_update_rights
    async def update_proctoring(
            self, *, proctoring_id: int, proctoring_data: PatchProctoringSchema
    ):
        await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)
        await self.get_subject_by_id_if_exist(subject_id=proctoring_data.subject_id)
        await self.get_user_by_id_if_exist(user_id=proctoring_data.user_id)

        await self.proctoring_db_service.update_proctoring(
            proctoring_id=proctoring_id, proctoring_data=proctoring_data
        )

    @check_delete_rights
    async def delete_proctoring_by_id(self, *, proctoring_id: int):
        await self.get_proctoring_by_id_if_exist(proctoring_id=proctoring_id)

        await self.proctoring_db_service.delete_proctoring_by_id(
            proctoring_id=proctoring_id
        )

    async def get_proctoring_type_by_id_if_exist(
            self, *, proctoring_type_id: int
    ) -> ProctoringTypeItemSchema:
        if proctoring_type := await self.proctoring_db_service.get_proctoring_type_by_id(
                proctoring_type_id=proctoring_type_id
        ):
            return ProctoringTypeItemSchema.model_validate(proctoring_type)
        raise ProctoringNotFoundError

    async def get_proctoring_by_id_if_exist(
            self, *, proctoring_id: int
    ) -> ProctoringItemSchema:
        if proctoring := await self.proctoring_db_service.get_proctoring_by_id(
                proctoring_id=proctoring_id
        ):
            return ProctoringItemSchema(
                proctoring_name=proctoring.proctoring_type.name,
                user_name=proctoring.user.full_name,
                subject_name=proctoring.subject.name,
                result_id=proctoring.result_id
            )
        raise ProctoringNotFoundError

    async def get_user_by_id_if_exist(self, *, user_id: int) -> UserItem:
        if user := await self.user_db_service.get_user_by_id(user_id=user_id):
            return user
        raise UserNotFoundError

    async def get_subject_by_id_if_exist(self, *, subject_id) -> SubjectSchema:
        if subject := await self.subject_db_service.get_subject_by_id(
                subject_id=subject_id
        ):
            return subject
        raise SubjectNotFoundError

    async def check_image(self, *, proctoring_id: int, image: UploadFile) -> None:
        if image.content_type.split("/")[0] != "image":
            raise NotImageError

        if not (proctoring := await self.proctoring_db_service.get_proctoring_by_id(
                proctoring_id=proctoring_id
        )):
            raise ProctoringNotFoundError

        image_array = np.frombuffer(await image.read(), np.uint8)

        result = handle_proctoring(img=image_array, proctoring_type=proctoring.proctoring_type)
        update_dict = {k: v for k, v in result.model_dump().items() if v is not False}

        await self.proctoring_result_db_service.set_new_proctoring_result(
            proctoring_result_id=proctoring.result_id, proctoring_result_data=update_dict
        )
