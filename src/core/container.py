from dependency_injector import containers, providers

from src.admin.infra.admin_repository import AdminRepository
from src.admin.service.get_personal_variables_service import GetPersonalVariablesService
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
from src.audiences.service.update_audience_exclude_status_service import (
    UpdateAudienceExcludeStatusService,
)
from src.audiences.service.update_audience_service import UpdateAudienceService
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
from src.campaign.infra.campaign_repository import CampaignRepository
from src.campaign.infra.campaign_set_repository import CampaignSetRepository
from src.campaign.infra.campaign_sqlalchemy_repository import CampaignSqlAlchemy
from src.campaign.service.approve_campaign_service import ApproveCampaignService
from src.campaign.service.confrim_campaign_set_group_message import (
    ConfirmCampaignSetGroupMessage,
)
from src.campaign.service.create_campaign_service import CreateCampaignService
from src.campaign.service.create_campaign_summary import CreateCampaignSummary
from src.campaign.service.create_recurring_campaign import CreateRecurringCampaign
from src.campaign.service.delete_campaign_service import DeleteCampaignService
from src.campaign.service.delete_image_for_message import DeleteImageForMessage
from src.campaign.service.generate_message_service import GenerateMessageService
from src.campaign.service.get_campaign_service import GetCampaignService
from src.campaign.service.get_campaign_set_description import GetCampaignSetDescription
from src.campaign.service.reserve_campaigns_service import ReserveCampaignsService
from src.campaign.service.test_meessage_send_service import TestMessageSendService
from src.campaign.service.update_campaign_progress_service import (
    UpdateCampaignProgressService,
)
from src.campaign.service.update_campaign_service import UpdateCampaignService
from src.campaign.service.update_campaign_set_message_group_service import (
    UpdateCampaignSetMessageGroupService,
)
from src.campaign.service.update_campaign_set_service import UpdateCampaignSetService
from src.campaign.service.update_campaign_set_status_to_confrim import (
    UpdateCampaignStatusToConfirm,
)
from src.campaign.service.update_message_use_status import UpdateMessageUseStatus
from src.campaign.service.upload_image_for_message import UploadImageForMessage
from src.common.infra.common_repository import CommonRepository
from src.common.infra.recommend_products_repository import RecommendProductsRepository
from src.common.utils.file.s3_service import S3Service
from src.common.utils.get_env_variable import get_env_variable
from src.contents.infra.contents_repository import ContentsRepository
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.service.add_contents_service import AddContentsService
from src.contents.service.add_creatives_service import AddCreativesService
from src.contents.service.delete_contents_service import DeleteContentsService
from src.contents.service.delete_creatives_service import DeleteCreativesService
from src.contents.service.generate_contents_service import GenerateContentsService
from src.contents.service.get_contents_service import GetContentsService
from src.contents.service.get_creative_recommendations_for_content import (
    GetCreativeRecommendationsForContent,
)
from src.contents.service.get_creatives_service import GetCreativesService
from src.contents.service.update_contents_service import UpdateContentsService
from src.contents.service.update_creatives_service import UpdateCreativesService
from src.dashboard.infra.dashboard_repository import DashboardRepository
from src.dashboard.infra.dashboard_sqlalchemy_repository import DashboardSqlAlchemy
from src.dashboard.service.get_audience_stats_service import GetAudienceStatsService
from src.dashboard.service.get_campaign_group_stats_service import (
    GetCampaignGroupStatsService,
)
from src.dashboard.service.get_campaign_stats_service import GetCampaignStatsService
from src.message_template.infra.message_template_repository import (
    MessageTemplateRepository,
)
from src.message_template.service.create_message_template_service import (
    CreateMessageTemplateService,
)
from src.message_template.service.delete_message_template_service import (
    DeleteMessageTemplateService,
)
from src.message_template.service.get_message_template_service import (
    GetMessageTemplateService,
)
from src.message_template.service.update_message_template_service import (
    UpdateMessageTemplateService,
)
from src.messages.infra.message_repository import MessageRepository
from src.messages.service.create_carousel_card import CreateCarouselCard
from src.messages.service.create_carousel_more_link import CreateCarouselMoreLink
from src.messages.service.delete_carousel_card import DeleteCarouselCard
from src.messages.service.message_service import MessageService
from src.offers.infra.offer_repository import OfferRepository
from src.offers.service.get_offer_service import GetOfferService
from src.offers.service.update_offer_service import UpdateOfferService
from src.payment.infra.credit_repository import CreditRepository
from src.payment.infra.deposit_repository import DepositRepository
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.infra.subscription_repository import SubscriptionRepository
from src.payment.service.billing_payment_service import BillingPaymentService
from src.payment.service.change_card_to_primary import ChangeCardToPrimaryService
from src.payment.service.delete_card_service import DeleteCardService
from src.payment.service.deposit_service import DepositService
from src.payment.service.get_card_service import GetCardService
from src.payment.service.get_credit_service import GetCreditService
from src.payment.service.get_payment_service import (
    CustomerKeyService,
)
from src.payment.service.get_subscription_service import GetSubscriptionService
from src.payment.service.invoice_download_service import InvoiceDownloadService
from src.payment.service.issue_billing_service import IssueBillingService
from src.payment.service.one_time_payment_service import OneTimePaymentService
from src.payment.service.save_pre_data_for_validation_service import (
    SavePreDataForValidationService,
)
from src.payment.service.toss_payment_gateway import TossPaymentGateway
from src.products.infra.product_repository import ProductRepository
from src.products.service.product_service import ProductService
from src.search.service.search_service import SearchService
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.infra.strategy_sqlalchemy_repository import StrategySqlAlchemy
from src.strategy.service.create_strategy_service import CreateStrategyService
from src.strategy.service.delete_strategy_service import DeleteStrategyService
from src.strategy.service.get_strategy_service import GetStrategyService
from src.strategy.service.update_strategy_service import UpdateStrategyService
from src.users.infra.user_repository import UserRepository
from src.users.infra.user_sqlalchemy import UserSqlAlchemy
from src.users.service.user_service import UserService

# class CachedFactory(providers.Factory):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._cache = lru_cache(maxsize=None)(self._provide)
#
#     def _provide(self, *args, **kwargs):
#         return super()._provide(*args, **kwargs)  # pyright: ignore [reportAttributeAccessIssue]
#
#     def __call__(self, *args, **kwargs):
#         return self._cache(*args, **kwargs)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.messages.routes.message_router",
            "src.auth.utils.get_current_user",
            "src.users.routes.user_router",
            "src.auth.routes.auth_router",
            "src.audiences.routes.audience_router",
            "src.audiences.service.background.execute_target_audience_summary",
            "src.auth.routes.onboarding_router",
            "src.campaign.routes.campaign_router",
            "src.campaign.routes.campaign_dag_router",
            "src.contents.routes.contents_router",
            "src.contents.routes.creatives_router",
            "src.search.routes.search_router",
            "src.strategy.routes.strategy_router",
            "src.offers.routes.offer_router",
            "src.message_template.routes.message_template_router",
            "src.admin.routes.admin_router",
            "src.products.routes.product_router",
            "src.dashboard.routes.dashboard_router",
            "src.payment.routes.payment_router",
        ]
    )

    """
    온보딩 의존성 주입
    """
    onboarding_sqlalchemy = providers.Factory(provides=OnboardingSqlAlchemyRepository)
    onboarding_repository = providers.Factory(
        provides=OnboardingRepository, onboarding_sqlalchemy=onboarding_sqlalchemy
    )
    onboarding_service = providers.Factory(
        provides=OnboardingService, onboarding_repository=onboarding_repository
    )

    """
    s3 객체
    """
    # todo 환경에 따라 버킷명 변경 필요
    bucket_name = get_env_variable("s3_asset_bucket")
    s3_asset_service = providers.Singleton(provides=S3Service, bucket_name=bucket_name)

    """
    사용자 의존성 주입
    """
    user_sqlalchemy = providers.Singleton(UserSqlAlchemy)
    user_repository = providers.Singleton(UserRepository, user_sqlalchemy=user_sqlalchemy)
    user_service = providers.Singleton(UserService, user_repository=user_repository)

    """
    인증 의존성 주입
    카페 24 의존성 주입
    """
    token_service = providers.Singleton(provides=TokenService)

    cafe24_sqlalchemy = providers.Singleton(Cafe24SqlAlchemyRepository)
    cafe24_repository = providers.Singleton(Cafe24Repository, cafe24_sqlalchemy=cafe24_sqlalchemy)

    cafe24_service = providers.Singleton(
        provides=Cafe24Service,
        user_repository=user_repository,
        cafe24_repository=cafe24_repository,
        onboarding_repository=onboarding_repository,
    )

    token_service = providers.Singleton(provides=TokenService)

    subscription_repository = providers.Singleton(provides=SubscriptionRepository)
    auth_service = providers.Singleton(
        provides=AuthService,
        token_service=token_service,
        user_repository=user_repository,
        subscription_repository=subscription_repository,
    )

    """
    Creatives 의존성 주입
    """
    creatives_sqlalchemy = providers.Singleton(CreativesSqlAlchemy)

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
    contents_sqlalchemy = providers.Singleton(provides=ContentsSqlAlchemy)

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

    generate_contents_service = providers.Singleton(
        provides=GenerateContentsService,
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
    audience_sqlalchemy = providers.Singleton(provides=AudienceSqlAlchemy)

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

    update_audience_service = providers.Singleton(
        provides=UpdateAudienceService, audience_repository=audience_repository
    )

    update_audience_exclude_service = providers.Singleton(
        provides=UpdateAudienceExcludeStatusService,
        audience_repository=audience_repository,
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
        provides=TargetAudienceSummarySqlAlchemy
    )

    """
    전략 의존성 주입
    """
    strategy_sqlalchemy = providers.Singleton(provides=StrategySqlAlchemy)

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
    offer_repository = providers.Singleton(provides=OfferRepository)

    get_offer_service = providers.Singleton(
        provides=GetOfferService,
        offer_repository=offer_repository,
        cafe24_repository=cafe24_repository,
    )

    update_offer_service = providers.Singleton(
        provides=UpdateOfferService, offer_repository=offer_repository
    )

    """
    캠페인 의존성 주입
    """

    campaign_sqlalchemy = providers.Singleton(provides=CampaignSqlAlchemy)

    campaign_repository = providers.Singleton(
        provides=CampaignRepository, campaign_sqlalchemy=campaign_sqlalchemy
    )

    common_repository = providers.Singleton(provides=CommonRepository)

    contents_sqlalchemy = providers.Singleton(provides=ContentsSqlAlchemy)

    contents_repository = providers.Singleton(
        ContentsRepository, contents_sqlalchemy=contents_sqlalchemy
    )

    campaign_set_repository = providers.Singleton(provides=CampaignSetRepository)

    get_campaign_service = providers.Singleton(
        provides=GetCampaignService,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    create_campaign_service = providers.Singleton(
        provides=CreateCampaignService,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
        strategy_repository=strategy_repository,
    )

    update_campaign_service = providers.Singleton(
        provides=UpdateCampaignService, campaign_repository=campaign_repository
    )

    generate_message_service = providers.Singleton(
        provides=GenerateMessageService,
        campaign_repository=campaign_repository,
        offer_repository=offer_repository,
        common_repository=common_repository,
        contents_repository=contents_repository,
    )

    update_campaign_set_service = providers.Singleton(
        provides=UpdateCampaignSetService,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    update_campaign_set_message_group_service = providers.Singleton(
        provides=UpdateCampaignSetMessageGroupService,
        campaign_repository=campaign_repository,
    )

    update_campaign_progress_service = providers.Singleton(
        provides=UpdateCampaignProgressService,
        campaign_repository=campaign_repository,
    )

    confirm_campaign_set_group_message = providers.Singleton(
        provides=ConfirmCampaignSetGroupMessage,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )
    update_message_use_status_service = providers.Singleton(
        provides=UpdateMessageUseStatus,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    get_campaign_set_description_service = providers.Singleton(
        provides=GetCampaignSetDescription,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    update_campaign_set_confirm_service = providers.Singleton(
        provides=UpdateCampaignStatusToConfirm,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    campaign_summary_service = providers.Singleton(
        provides=CreateCampaignSummary,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
        contents_repository=contents_repository,
    )

    credit_repository = providers.Singleton(provides=CreditRepository)

    approve_campaign_service = providers.Singleton(
        provides=ApproveCampaignService,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
        credit_repository=credit_repository,
        onboarding_repository=onboarding_repository,
    )

    test_send_service = providers.Singleton(provides=TestMessageSendService)

    delete_campaign_service = providers.Singleton(
        provides=DeleteCampaignService,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
    )

    reserve_campaign_service = providers.Singleton(
        provides=ReserveCampaignsService,
        approve_campaign_service=approve_campaign_service,
    )

    create_recurring_campaign_service = providers.Singleton(
        provides=CreateRecurringCampaign,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
        approve_campaign_service=approve_campaign_service,
        generate_message_service=generate_message_service,
    )

    """
    templates 의존성
    """
    message_template_repository = providers.Singleton(provides=MessageTemplateRepository)

    create_template_service = providers.Singleton(
        provides=CreateMessageTemplateService,
        message_template_repository=message_template_repository,
    )

    get_template_service = providers.Singleton(
        provides=GetMessageTemplateService,
        message_template_repository=message_template_repository,
    )

    update_template_service = providers.Singleton(
        provides=UpdateMessageTemplateService,
        message_template_repository=message_template_repository,
    )

    delete_template_service = providers.Singleton(
        provides=DeleteMessageTemplateService,
        message_template_repository=message_template_repository,
    )

    admin_repository = providers.Singleton(provides=AdminRepository)

    get_personal_variables_service = providers.Singleton(
        provides=GetPersonalVariablesService, admin_repository=admin_repository
    )

    """
    전략 삭제 및 업데이트
    """
    delete_strategy_service = providers.Singleton(
        provides=DeleteStrategyService,
        strategy_repository=strategy_repository,
        campaign_repository=campaign_repository,
    )

    update_strategy_service = providers.Singleton(
        provides=UpdateStrategyService,
        strategy_repository=strategy_repository,
    )

    """
    product 의존성
    """
    product_repository = providers.Singleton(provides=ProductRepository)

    product_service = providers.Singleton(
        provides=ProductService,
        product_repository=product_repository,
        creatives_repository=creatives_repository,
    )

    """
    search 의존성
    """
    recommend_products_repository = providers.Singleton(provides=RecommendProductsRepository)

    search_service = providers.Singleton(
        provides=SearchService,
        audience_repository=audience_repository,
        recommend_products_repository=recommend_products_repository,
        offer_repository=offer_repository,
        contents_repository=contents_repository,
        campaign_repository=campaign_repository,
        product_repository=product_repository,
        strategy_repository=strategy_repository,
        user_repository=user_repository,
    )

    """
    Dashboard 의존성
    """
    dashboard_sqlalchemy = providers.Singleton(provides=DashboardSqlAlchemy)

    dashboard_repository = providers.Singleton(
        provides=DashboardRepository, dashboard_sqlalchemy=dashboard_sqlalchemy
    )

    get_campaign_stats_service = providers.Singleton(
        provides=GetCampaignStatsService, dashboard_repository=dashboard_repository
    )

    get_campaign_group_stats_service = providers.Singleton(
        provides=GetCampaignGroupStatsService, dashboard_repository=dashboard_repository
    )

    get_audience_stats_service = providers.Singleton(
        provides=GetAudienceStatsService, dashboard_repository=dashboard_repository
    )

    """
    message 객체
    """
    message_repository = providers.Singleton(provides=MessageRepository)
    message_service = providers.Singleton(
        provides=MessageService,
        message_repository=message_repository,
        campaign_repository=campaign_repository,
    )

    """
    메시지에 사용할 이미지 업로드 의존성
    """
    upload_image_for_message = providers.Singleton(
        provides=UploadImageForMessage,
        campaign_repository=campaign_repository,
        campaign_set_repository=campaign_set_repository,
        message_service=message_service,
        s3_service=s3_asset_service,
    )

    delete_image_for_message = providers.Singleton(
        provides=DeleteImageForMessage,
        campaign_set_repository=campaign_set_repository,
        s3_service=s3_asset_service,
    )

    """
    결제
    """
    payment_repository = providers.Singleton(provides=PaymentRepository)

    save_pre_data_for_validation_service = providers.Singleton(
        provides=SavePreDataForValidationService, payment_repository=payment_repository
    )

    toss_payment_gateway = providers.Singleton(provides=TossPaymentGateway)

    one_time_payment_service = providers.Singleton(
        provides=OneTimePaymentService,
        payment_repository=payment_repository,
        payment_gateway=toss_payment_gateway,
        credit_repository=credit_repository,
        subscription_repository=subscription_repository,
    )

    issue_billing_service = providers.Singleton(
        provides=IssueBillingService,
        payment_repository=payment_repository,
        payment_gateway=toss_payment_gateway,
    )

    billing_payment_service = providers.Singleton(
        provides=BillingPaymentService,
        payment_repository=payment_repository,
        payment_gateway=toss_payment_gateway,
        subscription_repository=subscription_repository,
    )

    change_card_to_primary_service = providers.Singleton(
        provides=ChangeCardToPrimaryService,
        payment_repository=payment_repository,
    )

    get_card_service = providers.Singleton(
        provides=GetCardService,
        payment_repository=payment_repository,
    )

    delete_card_service = providers.Singleton(
        provides=DeleteCardService,
        payment_repository=payment_repository,
    )

    get_credit_service = providers.Singleton(
        provides=GetCreditService,
        payment_repository=payment_repository,
        credit_repository=credit_repository,
    )

    get_subscription_service = providers.Singleton(
        provides=GetSubscriptionService,
        payment_repository=payment_repository,
        subscription_repository=subscription_repository,
        common_repository=common_repository,
    )

    customer_key_service = providers.Singleton(
        provides=CustomerKeyService, payment_repository=payment_repository
    )

    deposit_repository = providers.Singleton(provides=DepositRepository)

    deposit_service = providers.Singleton(
        provides=DepositService,
        credit_repository=credit_repository,
        deposit_repository=deposit_repository,
    )

    invoice_download_service = providers.Singleton(
        provides=InvoiceDownloadService,
        payment_repository=payment_repository,
        credit_repository=credit_repository,
        deposit_repository=deposit_repository,
    )

    create_carousel_card = providers.Singleton(
        provides=CreateCarouselCard, message_repository=message_repository
    )

    delete_carousel_card = providers.Singleton(
        provides=DeleteCarouselCard, message_repository=message_repository
    )

    create_carousel_more_link = providers.Singleton(
        provides=CreateCarouselMoreLink,
        message_repository=message_repository,
    )
