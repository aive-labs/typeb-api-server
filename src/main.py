from auth.routes.auth_router import auth_router
from core.container import Container
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from users.routes.user_router import user_router


# FastAPI 앱 초기화
def create_app():
    container = Container()
    app = FastAPI()
    # app.container = container
    app.container = container

    return app


app = create_app()
app.include_router(user_router, prefix="/users")
app.include_router(router=auth_router, prefix='/auth')

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
