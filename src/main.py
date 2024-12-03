import time
import uuid

import sentry_sdk
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.admin.routes.admin_router import admin_router
from src.admin.routes.contact_router import contact_router
from src.audiences.routes.audience_router import audience_router
from src.auth.routes.auth_router import auth_router
from src.auth.routes.ga_router import ga_router
from src.auth.routes.onboarding_router import onboarding_router
from src.campaign.routes.campaign_dag_router import campaign_dag_router
from src.campaign.routes.campaign_router import campaign_router
from src.common.utils.get_env_variable import get_env_variable
from src.contents.routes.contents_router import contents_router
from src.contents.routes.creatives_router import creatives_router
from src.core.container import Container
from src.core.contextvars_context import correlation_id_var
from src.core.exceptions.register_exception_handler import register_exception_handlers
from src.core.logging import logger
from src.core.middleware.prometheus import PrometheusMiddleware, metrics
from src.dashboard.routes.dashboard_router import dashboard_router
from src.message_template.routes.message_template_router import message_template_router
from src.messages.routes.message_router import message_router
from src.messages.routes.ppurio_message_router import ppurio_message_router
from src.offers.routes.offer_router import offer_router
from src.payment.routes.payment_router import payment_router
from src.products.routes.product_router import product_router
from src.search.routes.search_router import search_router
from src.strategy.routes.strategy_router import strategy_router
from src.users.routes.user_router import user_router


# FastAPI 앱 초기화
def create_app():
    app = FastAPI()
    print("Create Dependency Container.")
    container = Container()
    app.container = container  # pyright: ignore [reportAttributeAccessIssue]

    return app


env_profile = get_env_variable("env")

if env_profile != "local":
    sentry_sdk.init(
        dsn="https://2d53fe5b3523ee71d36b86baa929a6f6@o4508169200205824.ingest.us.sentry.io/4508169206235136",
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,  # traces_sample_rate to 1.0 to capture 100%
        _experiments={
            "continuous_profiling_auto_start": True,
        },
        environment=env_profile,
    )

app = create_app()
app.include_router(router=auth_router, prefix="/api/v1/auth")
app.include_router(router=onboarding_router, prefix="/api/v1/auth/onboarding")
app.include_router(router=user_router, prefix="/api/v1/users")
app.include_router(router=ga_router, prefix="/api/v1/ga")
app.include_router(router=campaign_router, prefix="/api/v1/campaign-management")
app.include_router(router=campaign_dag_router, prefix="/api/v1/campaign-dag")
app.include_router(router=creatives_router, prefix="/api/v1/contents-management/creatives")
app.include_router(router=contents_router, prefix="/api/v1/contents-management/contents")
app.include_router(router=audience_router, prefix="/api/v1/audience-management")
app.include_router(router=strategy_router, prefix="/api/v1/strategy-management")
app.include_router(router=search_router, prefix="/api/v1/search")
app.include_router(router=message_router, prefix="/api/v1/message")
app.include_router(router=ppurio_message_router, prefix="/message")
app.include_router(router=offer_router, prefix="/api/v1/settings/offers")
app.include_router(router=message_template_router, prefix="/api/v1/settings/templates")
app.include_router(router=admin_router, prefix="/api/v1/settings/admin")
app.include_router(router=product_router, prefix="/api/v1/products")
app.include_router(router=dashboard_router, prefix="/api/v1/dashboard")
app.include_router(router=payment_router, prefix="/api/v1/payment")
app.include_router(router=contact_router, prefix="/api/v1/contact-us")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.add_middleware(PrometheusMiddleware, app_name="aace-api-server")
app.add_route("/pringles", metrics)


# 상관 ID 미들웨어
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4()).replace("-", "")[:8]
    request.state.correlation_id = correlation_id
    correlation_id_var.set(correlation_id)

    # 요청 바디를 읽고 저장
    request_body = await request.body()
    request.state.body = request_body

    # 요청 바디를 다시 읽을 수 있도록 스트림 재설정
    async def receive():
        return {"type": "http.request", "body": request_body, "more_body": False}

    request._receive = receive

    # 요청 정보 로그
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(
            f"Exception in {request.method} {request.url.path}: {exc}",
            exc_info=True,
            extra={"correlation_id": correlation_id},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "correlation_id": correlation_id},
        )

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms",
        extra={"correlation_id": correlation_id},
    )
    return response


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy"}
