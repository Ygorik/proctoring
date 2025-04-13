from fastapi import FastAPI
from src.services.user.routers.router_v1 import router as registration_router
from src.services.authorization.routers.router_v1 import router as authorization_router
from src.services.role.routers.router_v1 import router as role_router
from src.services.token.routers.router_v1 import router as token_router
from src.services.subject.routers.router_v1 import router as subject_router
from src.services.proctoring.routers.router_v1 import router as proctoring_router
from src.services.proctoring_result.routers.router_v1 import (
    router as proctoring_result_router,
)


app = FastAPI()

app.include_router(token_router, prefix="/api/v1/token", tags=["Token"])

app.include_router(role_router, prefix="/api/v1/role", tags=["Role"])

app.include_router(
    authorization_router, prefix="/api/v1/authorization", tags=["User | Authorization"]
)
app.include_router(registration_router, prefix="/api/v1/user", tags=["User"])

app.include_router(subject_router, prefix="/api/v1/subject", tags=["Subject"])

app.include_router(proctoring_router, prefix="/api/v1/proctoring", tags=["Proctoring"])
app.include_router(
    proctoring_result_router,
    prefix="/api/v1/proctoring-result",
    tags=["Proctoring | Result"],
)
