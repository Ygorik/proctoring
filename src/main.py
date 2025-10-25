from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.services.user.routers.router_v1 import router as registration_router
from src.services.authorization.routers.router_v1 import router as authorization_router
from src.services.role.routers.router_v1 import router as role_router
from src.services.token.routers.router_v1 import router as token_router
from src.services.subject.routers.router_v1 import router as subject_router
from src.services.proctoring.routers.router_v1 import router as proctoring_router
from src.services.proctoring_result.routers.router_v1 import (
    router as proctoring_result_router,
)
from src.services.snapshot.routers.router_v1 import router as snapshot_router


app = FastAPI()

# Указываем разрешенные источники (frontend)
origins = [
    "http://localhost:3000",  # React dev сервер
    "http://127.0.0.1:3000",  # на всякий случай
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # откуда разрешены запросы
    allow_credentials=True,
    allow_methods=["*"],               # какие методы разрешены (GET, POST и т.д.)
    allow_headers=["*"],               # какие заголовки разрешены (например, Authorization)
)

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
app.include_router(
    snapshot_router, 
    prefix="/api/v1/proctoring",  # Используем тот же префикс для единообразия
    tags=["Proctoring | Snapshots"]
)
