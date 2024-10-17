import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request

from src.admin.routes.admin_router import admin_router
from src.admin.routes.contact_router import contact_router
from src.audiences.routes.audience_router import audience_router
from src.auth.routes.auth_router import auth_router
from src.auth.routes.onboarding_router import onboarding_router
from src.campaign.routes.campaign_dag_router import campaign_dag_router
from src.campaign.routes.campaign_router import campaign_router
from src.contents.routes.contents_router import contents_router
from src.contents.routes.creatives_router import creatives_router
from src.core.container import Container
from src.core.exceptions.register_exception_handler import register_exception_handlers
from src.dashboard.routes.dashboard_router import dashboard_router
from src.message_template.routes.message_template_router import message_template_router
from src.messages.routes.message_router import message_router
from src.offers.routes.offer_router import offer_router
from src.payment.routes.payment_router import payment_router
from src.products.routes.product_router import product_router
from src.search.routes.search_router import search_router
from src.strategy.routes.strategy_router import strategy_router
from src.users.routes.user_router import user_router


# FastAPI 앱 초기화
def create_app():
    app = FastAPI()
    print("create container..")
    container = Container()
    # container.init_resources()
    # print("initailize container..")
    app.container = container  # pyright: ignore [reportAttributeAccessIssue]

    return app


app = create_app()
app.include_router(router=auth_router, prefix="/auth")
app.include_router(router=onboarding_router, prefix="/auth/onboarding")
app.include_router(router=user_router, prefix="/users")
app.include_router(router=campaign_router, prefix="/campaign-management")
app.include_router(router=campaign_dag_router, prefix="/campaign-dag")
app.include_router(router=creatives_router, prefix="/contents-management/creatives")
app.include_router(router=contents_router, prefix="/contents-management/contents")
app.include_router(router=audience_router, prefix="/audience-management")
app.include_router(router=strategy_router, prefix="/strategy-management")
app.include_router(router=search_router, prefix="/search")
app.include_router(router=message_router, prefix="/message")
app.include_router(router=offer_router, prefix="/settings/offers")
app.include_router(router=message_template_router, prefix="/settings/templates")
app.include_router(router=admin_router, prefix="/settings/admin")
app.include_router(router=product_router, prefix="/products")
app.include_router(router=dashboard_router, prefix="/dashboard")
app.include_router(router=payment_router, prefix="/payment")
app.include_router(router=contact_router, prefix="/contact-us")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

Instrumentator().instrument(app).expose(app, endpoint="/pringles")
# HTTP 요청 횟수
REQUEST_COUNT = Counter(
    "http_request_count", "Number of HTTP requests received", ["method", "endpoint"]
)

# 요청 실패 수 (상태 코드별)
ERROR_COUNT = Counter(
    "http_error_count", "Number of HTTP errors encountered", ["method", "endpoint", "status_code"]
)

# 요청 응답 지연 시간
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency in seconds", ["method", "endpoint"]
)

# 현재 활성 사용자 수
ACTIVE_USERS = Gauge("active_users", "Number of active users currently connected")

# 메모리 및 CPU 사용량
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage in percent")
MEMORY_USAGE = Gauge("memory_usage_mb", "Memory usage in MB")
MAX_MEMORY = Gauge("max_memory_mb", "Maximum Memory in MB")
MAX_MEMORY.set(psutil.virtual_memory().total / (1024 * 1024))


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    # 활성 사용자 수 증가
    ACTIVE_USERS.inc()

    # 요청 메트릭 기록 시작
    method = request.method
    endpoint = request.url.path

    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        response = await call_next(request)

    # 요청 횟수 기록
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    # 오류 상태 코드 기록
    if response.status_code >= 400:
        ERROR_COUNT.labels(method=method, endpoint=endpoint, status_code=response.status_code).inc()

    # 활성 사용자 수 감소
    ACTIVE_USERS.dec()

    return response


# 시스템 메트릭을 주기적으로 업데이트 하는 함수
def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().used / (1024 * 1024))


#  APScheduler to call update_system_metrics 30초 간격으로 업데이트
scheduler = BackgroundScheduler()
scheduler.add_job(update_system_metrics, "interval", seconds=5)
scheduler.start()


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy"}
