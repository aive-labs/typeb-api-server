from dependency_injector import containers, providers

from core.database import Database, get_db_url
from users.infra.user_repository import UserRepository
from users.infra.user_sqlalchemy import UserSqlAlchemy
from users.service.user_service import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["users.routes.user_router"])

    db = providers.Singleton(Database, db_url=get_db_url())

    user_sqlalchemy = providers.Factory(UserSqlAlchemy, db=db.provided.session)
    user_repository = providers.Factory(UserRepository, user_sqlalchemy=user_sqlalchemy)
    user_service = providers.Factory(UserService, user_repository=user_repository)
