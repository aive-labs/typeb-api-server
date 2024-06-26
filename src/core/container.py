from dependency_injector import containers, providers

from src.audiences.infra.audience_repository import AudienceRepository
from src.audiences.infra.audience_sqlalchemy_repository import AudienceSqlAlchemy
from src.audiences.service.background.target_audience_summary_sqlalchemy import (
    TargetAudienceSummarySqlAlchemy,
)
from src.audiences.service.create_audience_service import CreateAudienceService
from src.audiences.service.csv_upload_audience_service import CSVUploadAudienceService
from src.audiences.service.delete_audience_service import DeleteAudienceService
from src.audiences.service.download_audience_service import DownloadAudienceService
from src.audiences.service.get_audience_creation_options import (
    GetAudienceCreationOptions,
)
from src.audiences.service.get_audience_service import GetAudienceService
from src.audiences.service.update_cycle_service import AudienceUpdateCycleService
from src.auth.infra.cafe24_repository import Cafe24Repository
from src.auth.infra.cafe24_sqlalchemy_repository import Cafe24SqlAlchemyRepository
from src.auth.infra.onboarding_repository import OnboardingRepository
from src.auth.infra.onboarding_sqlalchemy_repository import (
    OnboardingSqlAlchemyRepository,
)
from src.auth.service.auth_service import AuthService
from src.auth.service.cafe24_service import Cafe24Service
from src.auth.service.onboarding_service import OnboardingService
from src.auth.service.token_service import TokenService
from src.common.infra.recommend_products_repository import RecommendProductsRepository
from src.common.utils.file.s3_service import S3Service
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.service.add_contents_service import AddContentsService
from src.contents.service.add_creatives_service import AddCreativesService
from src.contents.service.delete_contents_service import DeleteContentsService
from src.contents.service.delete_creatives_service import DeleteCreativesService
from src.contents.service.get_contents_service import GetContentsService
from src.contents.service.get_creative_recommendations_for_content import (
    GetCreativeRecommendationsForContent,
)
from src.contents.service.get_creatives_service import GetCreativesService
from src.contents.service.update_contents_service import UpdateContentsService
from src.contents.service.update_creatives_service import UpdateCreativesService
from src.core.database import Database, get_db_url
from src.message_template.infra.message_template_repository import (
    MessageTemplateRepository,
)
from src.message_template.service.create_message_template_service import (
    CreateMessageTemplateService,
)
from src.messages.infra.ppurio_message_repository import PpurioMessageRepository
from src.messages.service.message_service import MessageService
from src.offers.infra.offer_repository import OfferRepository
from src.offers.service.get_offer_service import GetOfferService
from src.offers.service.update_offer_service import UpdateOfferService
from src.search.service.search_service import SearchService
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.infra.strategy_sqlalchemy_repository import StrategySqlAlchemy
from src.strategy.service.create_strategy_service import CreateStrategyService
from src.strategy.service.get_strategy_service import GetStrategyService
from src.users.infra.user_repository import UserRepository
from src.users.infra.user_sqlalchemy import UserSqlAlchemy
from src.users.service.user_service import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.messages.routes.message_router",
            "src.auth.utils.get_current_user",
            "src.users.routes.user_router",
            "src.auth.routes.auth_router",
            "src.auth.routes.onboarding_router",
            "src.contents.routes.contents_router",
            "src.contents.routes.creatives_router",
            "src.audiences.routes.audience_router",
            "src.audiences.service.background.execute_target_audience_summary",
            "src.strategy.routes.strategy_router",
            "src.search.routes.search_router",
            "src.offers.routes.offer_router",
            "src.message_template.routes.message_template_router",
        ]
    )

    """
    config 파일에 따라 다른 데이터베이스 주입
    """
    db = providers.Singleton(Database, db_url=get_db_url())
    print(db.provided._create_database())

    """
    s3 객체
    """
    # todo 환경에 따라 버킷명 변경 필요
    s3_asset_service = providers.Singleton(
        provides=S3Service, bucket_name="aice-asset-dev"
    )

    """
    message 객체
    """
    message_repository = providers.Singleton(
        provides=PpurioMessageRepository, db=db.provided.session
    )
    message_service = providers.Singleton(
        provides=MessageService, message_repository=message_repository
    )

    """
    사용자 의존성 주입
    """
    user_sqlalchemy = providers.Singleton(UserSqlAlchemy, db=db.provided.session)
    user_repository = providers.Singleton(
        UserRepository, user_sqlalchemy=user_sqlalchemy
    )
    user_service = providers.Singleton(UserService, user_repository=user_repository)

    """
    온보딩 의존성 주입
    """
    onboarding_sqlalchemy = providers.Singleton(
        provides=OnboardingSqlAlchemyRepository, db=db.provided.session
    )
    onboarding_repository = providers.Singleton(
        provides=OnboardingRepository, onboarding_sqlalchemy=onboarding_sqlalchemy
    )
    onboarding_service = providers.Singleton(
        provides=OnboardingService, onboarding_repository=onboarding_repository
    )

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
        onboarding_repository=onboarding_repository,
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
        provides=AddContentsService,
        contents_repository=contents_repository,
        user_repository=user_repository,
        cafe24_repository=cafe24_repository,
        s3_service=s3_asset_service,
    )

    get_contents_service = providers.Singleton(
        provides=GetContentsService,
        contents_repository=contents_repository,
    )

    get_creative_recommendation = providers.Singleton(
        provides=GetCreativeRecommendationsForContent,
        creatives_repository=creatives_repository,
        s3_service=s3_asset_service,
    )

    update_contents_service = providers.Singleton(
        provides=UpdateContentsService,
        contents_repository=contents_repository,
        user_repository=user_repository,
        cafe24_repository=cafe24_repository,
        s3_service=s3_asset_service,
    )

    delete_contents_service = providers.Singleton(
        provides=DeleteContentsService,
        contents_repository=contents_repository,
        s3_service=s3_asset_service,
    )

    """
    타겟 오디언스 의존성 주입
    """
    audience_sqlalchemy = providers.Singleton(
        provides=AudienceSqlAlchemy, db=db.provided.session
    )

    audience_repository = providers.Singleton(
        provides=AudienceRepository, audience_sqlalchemy=audience_sqlalchemy
    )

    get_audience_service = providers.Singleton(
        provides=GetAudienceService, audience_repository=audience_repository
    )

    get_audience_creation_option = providers.Singleton(
        provides=GetAudienceCreationOptions, audience_repository=audience_repository
    )

    create_audience_service = providers.Singleton(
        provides=CreateAudienceService, audience_repository=audience_repository
    )

    delete_audience_service = providers.Singleton(
        provides=DeleteAudienceService, audience_repository=audience_repository
    )

    download_audience_service = providers.Singleton(
        provides=DownloadAudienceService, audience_repository=audience_repository
    )

    csv_upload_service = providers.Singleton(
        provides=CSVUploadAudienceService, audience_repository=audience_repository
    )

    audience_update_cycle_service = providers.Singleton(
        provides=AudienceUpdateCycleService, audience_repository=audience_repository
    )

    """
    타겟 오디언스 백그라운드 태스크
    """
    target_audience_summary_sqlalchemy = providers.Singleton(
        provides=TargetAudienceSummarySqlAlchemy, db=db.provided.session
    )

    """
    전략 의존성 주입
    """
    strategy_sqlalchemy = providers.Singleton(
        provides=StrategySqlAlchemy, db=db.provided.session
    )

    strategy_repository = providers.Singleton(
        provides=StrategyRepository, strategy_sqlalchemy=strategy_sqlalchemy
    )

    get_strategy_service = providers.Singleton(
        provides=GetStrategyService,
        strategy_repository=strategy_repository,
    )

    create_strategy_service = providers.Singleton(
        provides=CreateStrategyService, strategy_repository=strategy_repository
    )

    """
    offer 의존성
    """
    offer_repository = providers.Singleton(
        provides=OfferRepository, db=db.provided.session
    )

    get_offer_service = providers.Singleton(
        provides=GetOfferService, offer_repository=offer_repository
    )

    update_offer_service = providers.Singleton(
        provides=UpdateOfferService, offer_repository=offer_repository
    )

    """
    template 의존성
    """
    message_template_repository = providers.Singleton(
        provides=MessageTemplateRepository, db=db.provided.session
    )
    create_template_service = providers.Singleton(
        provides=CreateMessageTemplateService,
        message_template_repository=message_template_repository,
    )

    """
    search 의존성
    """
    recommend_products_repository = providers.Singleton(
        provides=RecommendProductsRepository, db=db.provided.session
    )

    search_service = providers.Singleton(
        provides=SearchService,
        audience_repository=audience_repository,
        recommend_products_repository=recommend_products_repository,
        offer_repository=offer_repository,
    )

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
