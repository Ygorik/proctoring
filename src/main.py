from fastapi import FastAPI
from src.services.registration.routers.router_v1 import router as registration_router
from src.services.authorization.routers.router_v1 import router as authorization_router
from src.services.role.routers.router_v1 import router as role_router
from src.services.token.routers.router_v1 import router as token_router


app = FastAPI()

app.include_router(token_router, prefix="/api/v1/token", tags=["Token"])

app.include_router(role_router, prefix="/api/v1/role", tags=["Role"])

app.include_router(
    registration_router, prefix="/api/v1/registration", tags=["User | Registration"]
)
app.include_router(
    authorization_router, prefix="/api/v1/authorization", tags=["User | Authorization"]
)
