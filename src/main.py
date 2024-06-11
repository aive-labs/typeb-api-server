import logging

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routes.auth_router import auth_router
from src.contents.routes.creatives_router import creatives_router
from src.core.container import Container
from src.users.routes.user_router import user_router


# FastAPI 앱 초기화
def create_app():
    logging.basicConfig(level=logging.INFO)
    app = FastAPI()
    app.container = Container()  # pyright: ignore [reportAttributeAccessIssue]
    return app


app = create_app()
app.include_router(router=user_router, prefix="/users")
app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=creatives_router, prefix="/contents-management/creatives")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy"}
