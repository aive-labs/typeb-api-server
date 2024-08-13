from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.admin.routes.admin_router import admin_router
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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


# @app.middleware("http")
# async def set_schema_middleware(request: Request, call_next):
#     # Get the schema name from request headers (default to 'default_schema')
#     schema_name = request.headers.get("X-Schema", "aivelabs_sv")
#     # Set the schema in the context variable
#     schema_context.set(schema_name)
#     schema_name = schema_context.get()
#     print(f"[middleware] {schema_name}")
#     # Process the request
#     response = await call_next(request)
#     return response


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "healthy"}
