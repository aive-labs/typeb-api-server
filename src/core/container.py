from auth.service.auth_service import AuthService
from auth.service.token_service import TokenService
from core.database import Database, get_db_url
from dependency_injector import containers, providers
from users.infra.user_repository import UserRepository
from users.infra.user_sqlalchemy import UserSqlAlchemy
from users.service.user_service import UserService

from src.audiences.infra.audience_sqlalchemy_repository import AudienceSqlAlchemy
from src.audiences.routes.port.usecase.create_audience_usecase import (
    CreateAudienceUsecase,
)
from src.audiences.routes.port.usecase.delete_audience_usecase import (
    DeleteAudienceUsecase,
)
from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUsecase
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.contents.routes.port.usecase.add_creatives_usecase import AddCreativesUseCase
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase
from src.contents.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.strategy.infra.strategy_sqlalchemy_repository import StrategySqlAlchemy
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUsecase
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUsecase
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "users.routes.user_router",
            "auth.routes.auth_router",
            "contents.routes.contents_router",
            "contents.routes.creatives_router",
        ]
    )

    """
    config 파일에 따라 다른 데이터베이스 주입
    """

    db = providers.Singleton(Database, db_url=get_db_url())

    """
    사용자 의존성 주입
    """
    user_sqlalchemy = providers.Factory(UserSqlAlchemy, db=db.provided.session)
    user_repository = providers.Factory(UserRepository, user_sqlalchemy=user_sqlalchemy)
    user_service = providers.Factory(UserService, user_repository=user_repository)

    """
    인증 의존성 주입
    """
    token_service = providers.Factory(provides=TokenService)
    auth_service = providers.Factory(
        provides=AuthService,
        token_service=token_service,
        user_repository=user_repository,
    )

    """
    Creatives 의존성 주입
    """
    add_creatives_service = providers.Factory(
        provides=AddCreativesUseCase, user_repository=user_repository
    )

    get_creatives_service = providers.Factory(
        provides=GetCreativesUseCase, user_repository=user_repository
    )

    """
    컨텐츠 의존성 주입
    """
    contents_sqlalchemy = providers.Factory(
        provides=ContentsSqlAlchemy, db=db.provided.session
    )

    contents_repository = providers.Singleton(
        ContentsRepository, contents_sqlalchemy=contents_sqlalchemy
    )

    add_contents_service = providers.Factory(
        provides=AddContentsUseCase,
        contents_repository=contents_repository,
        user_repository=user_repository,
    )

    get_contents_service = providers.Factory(
        provides=GetContentsUseCase,
        contents_repository=contents_repository,
        user_repository=user_repository,
    )

    """
    타겟 오디언스 의존성 주입
    """
    audience_sqlalchemy = providers.Singleton(
        provides=AudienceSqlAlchemy, db=db.provided.session
    )

    audience_repository = providers.Singleton(
        provides=BaseAudienceRepository, audience_sqlalchemy=audience_sqlalchemy
    )

    get_audience_service = providers.Singleton(
        provides=GetAudienceUsecase, audience_repository=audience_repository
    )

    create_audience_service = providers.Singleton(
        provides=CreateAudienceUsecase, audience_repository=audience_repository
    )

    delete_audience_service = providers.Singleton(
        provides=DeleteAudienceUsecase, audience_repository=audience_repository
    )

    """
    전략 의존성 주입
    """
    strategy_sqlalchemy = providers.Singleton(
        provides=StrategySqlAlchemy, db=db.provided.sesssion
    )

    strategy_repository = providers.Singleton(
        provides=BaseStrategyRepository, strategy_sqlalchemy=strategy_sqlalchemy
    )

    get_strategy_service = providers.Singleton(
        provides=GetStrategyUsecase,
        strategy_repository=strategy_repository,
    )

    create_strategy_service = providers.Singleton(
        provides=CreateStrategyUsecase, strategy_repository=strategy_repository
    )
