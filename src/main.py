from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from core.container import Container
from users.routes import user_router

from users.routes.user_router import user_router


def create_app():
    container = Container()
    app = FastAPI()
    setattr(app, "container", container)
    return app


app = create_app()
app.include_router(user_router, prefix="/users")

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
