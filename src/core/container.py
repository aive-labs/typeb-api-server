from auth.service.auth_service import AuthService
from auth.service.token_service import TokenService
from core.database import Database, get_db_url
from dependency_injector import containers, providers
from users.infra.user_repository import UserRepository
from users.infra.user_sqlalchemy import UserSqlAlchemy
from users.service.user_service import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["users.routes.user_router",
                                                            "auth.routes.auth_router"])

    # config 파일에 따라 다른 데이터베이스 주입
    db = providers.Singleton(Database, db_url=get_db_url())

    user_sqlalchemy = providers.Factory(UserSqlAlchemy, db=db.provided.session)
    user_repository = providers.Factory(UserRepository, user_sqlalchemy=user_sqlalchemy)
    user_service = providers.Factory(UserService, user_repository=user_repository)

    token_service = providers.Factory(provides=TokenService)
    auth_service = providers.Factory(provides=AuthService, token_service=token_service, user_repository=user_repository)
