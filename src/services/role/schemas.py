from src.base_schemas import BaseResponseSchemas


class CreateRoleSchema(BaseResponseSchemas):
    name: str
    rights_create: bool
    rights_read: bool
    rights_update: bool
    rights_delete: bool


class PatchRoleSchema(BaseResponseSchemas):
    name: str | None = None
    rights_create: bool | None = None
    rights_read: bool | None = None
    rights_update: bool | None = None
    rights_delete: bool | None = None


class RoleItemSchema(CreateRoleSchema):
    id: int
