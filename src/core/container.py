from dependency_injector import containers, providers

from src.auth.infra.cafe24_repository import Cafe24Repository
from src.auth.infra.cafe24_sqlalchemy_repository import Cafe24SqlAlchemyRepository
from src.auth.service.auth_service import AuthService
from src.auth.service.cafe24_service import Cafe24Service
from src.auth.service.token_service import TokenService
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase
from src.contents.service.add_creatives_service import AddCreativesService
from src.contents.service.delete_creatives_service import DeleteCreativesService
from src.contents.service.get_creatives_service import GetCreativesService
from src.contents.service.update_creatives_service import UpdateCreativesService
from src.core.database import Database, get_db_url
from src.users.infra.user_repository import UserRepository
from src.users.infra.user_sqlalchemy import UserSqlAlchemy
from src.users.service.user_service import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.auth.utils.get_current_user",
            "src.users.routes.user_router",
            "src.auth.routes.auth_router",
            "src.contents.routes.contents_router",
            "src.contents.routes.creatives_router",
        ]
    )

    """
    config 파일에 따라 다른 데이터베이스 주입
    """

    db = providers.Singleton(Database, db_url=get_db_url())

    """
    사용자 의존성 주입
    """
    user_sqlalchemy = providers.Singleton(UserSqlAlchemy, db=db.provided.session)
    user_repository = providers.Singleton(
        UserRepository, user_sqlalchemy=user_sqlalchemy
    )
    user_service = providers.Singleton(UserService, user_repository=user_repository)

    """
    인증 의존성 주입
    카페 24 의존성 주입
    """

    token_service = providers.Singleton(provides=TokenService)

    cafe24_sqlalchemy = providers.Singleton(
        Cafe24SqlAlchemyRepository, db=db.provided.session
    )
    cafe24_repository = providers.Singleton(
        Cafe24Repository, cafe24_sqlalchemy=cafe24_sqlalchemy
    )

    cafe24_service = providers.Singleton(
        provides=Cafe24Service,
        user_repository=user_repository,
        cafe24_repository=cafe24_repository,
    )

    token_service = providers.Singleton(provides=TokenService)
    auth_service = providers.Singleton(
        provides=AuthService,
        token_service=token_service,
        user_repository=user_repository,
    )

    """
    Creatives 의존성 주입
    """

    creatives_sqlalchemy = providers.Singleton(
        CreativesSqlAlchemy, db=db.provided.session
    )

    creatives_repository = providers.Singleton(
        CreativesRepository, creative_sqlalchemy=creatives_sqlalchemy
    )

    add_creatives_service = providers.Singleton(
        provides=AddCreativesService,
        creatives_repository=creatives_repository,
        cafe24_repository=cafe24_repository,
    )

    get_creatives_service = providers.Singleton(
        provides=GetCreativesService, creatives_repository=creatives_repository
    )

    update_creatives_service = providers.Singleton(
        provides=UpdateCreativesService, creatives_repository=creatives_repository
    )
    delete_creatives_service = providers.Singleton(
        provides=DeleteCreativesService, creatives_repository=creatives_repository
    )

    """
    컨텐츠 의존성 주입
    """
    contents_sqlalchemy = providers.Singleton(
        provides=ContentsSqlAlchemy, db=db.provided.session
    )

    contents_repository = providers.Singleton(
        ContentsRepository, contents_sqlalchemy=contents_sqlalchemy
    )

    add_contents_service = providers.Singleton(
        provides=AddContentsUseCase,
        contents_repository=contents_repository,
        user_repository=user_repository,
    )

    get_contents_service = providers.Singleton(
        provides=GetContentsUseCase,
        contents_repository=contents_repository,
        user_repository=user_repository,
    )

    """
    타겟 오디언스 의존성 주입
    """
    # audience_sqlalchemy = providers.Singleton(
    #     provides=AudienceSqlAlchemy, db=db.provided.session
    # )
    #
    # audience_repository = providers.Singleton(
    #     provides=BaseAudienceRepository, audience_sqlalchemy=audience_sqlalchemy
    # )
    #
    # get_audience_service = providers.Singleton(
    #     provides=GetAudienceUsecase, audience_repository=audience_repository
    # )
    #
    # create_audience_service = providers.Singleton(
    #     provides=CreateAudienceUsecase, audience_repository=audience_repository
    # )
    #
    # delete_audience_service = providers.Singleton(
    #     provides=DeleteAudienceUsecase, audience_repository=audience_repository
    # )

    """
    전략 의존성 주입
    """
    # strategy_sqlalchemy = providers.Singleton(
    #     provides=StrategySqlAlchemy, db=db.provided.sesssion
    # )
    #
    # strategy_repository = providers.Singleton(
    #     provides=BaseStrategyRepository, strategy_sqlalchemy=strategy_sqlalchemy
    # )
    #
    # get_strategy_service = providers.Singleton(
    #     provides=GetStrategyUsecase,
    #     strategy_repository=strategy_repository,
    # )
    #
    # create_strategy_service = providers.Singleton(
    #     provides=CreateStrategyUsecase, strategy_repository=strategy_repository
    # )

    """
    캠페인 의존성 주입
    """

    # campaign_sqlalchemy = providers.Singleton(
    #     provides=CampaignSqlAlchemy, db=db.provided.session
    # )
    #
    # campaign_repository = providers.Singleton(
    #     provides=BaseCampaignRepository, campaign_sqlalchemy=campaign_sqlalchemy
    # )
    #
    # get_campaign_service = providers.Singleton(
    #     provides=GetCampaignUsecase, campaign_repository=campaign_repository
    # )
    #
    # create_campaign_service = providers.Singleton(
    #     provides=CreateCampaignUsecase, campaign_repository=campaign_repository
    # )
