from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.audiences.routes.audience_router import audience_router
from src.auth.routes.auth_router import auth_router
from src.auth.routes.onboarding_router import onboarding_router
from src.contents.routes.contents_router import contents_router
from src.contents.routes.creatives_router import creatives_router
from src.core.container import Container
from src.users.routes.user_router import user_router


# FastAPI 앱 초기화
def create_app():
    app = FastAPI()
    app.container = Container()  # pyright: ignore [reportAttributeAccessIssue]
    return app


app = create_app()
app.include_router(router=user_router, prefix="/users")
app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=onboarding_router, prefix="/auth/onboarding_response.py")
app.include_router(router=creatives_router, prefix="/contents-management/creatives")
app.include_router(router=contents_router, prefix="/contents-management/contents")
app.include_router(router=audience_router, prefix="/audience-management")

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
