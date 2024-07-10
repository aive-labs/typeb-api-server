from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.enums.campaign_media import CampaignMedia
from src.core.container import Container
from src.core.database import get_db_session
from src.message_template.enums.kakao_button_type import KakaoButtonType
from src.message_template.enums.message_type import MessageType
from src.message_template.routes.dto.response.kakao_button_link import KakaoButtonLink
from src.strategy.routes.dto.request.preview_message_create import PreviewMessageCreate
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.dto.response.preview_message_response import (
    PreviewMessage,
    PreviewMessageResponse,
)
from src.strategy.routes.dto.response.strategy_response import StrategyResponse
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUseCase
from src.strategy.routes.port.delete_strategy_usecase import DeleteStrategyUseCase
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUseCase
from src.strategy.routes.port.update_strategy_usecase import UpdateStrategyUseCase

strategy_router = APIRouter(tags=["Strategy-management"])


@strategy_router.get("/strategies")
@inject
def get_strategies(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db_session),
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
) -> list[StrategyResponse]:
    return get_strategy_service.get_strategies(start_date, end_date, user, db=db)


@strategy_router.get("/strategies/{strategy_id}")
@inject
def read_strategy_object(
    strategy_id: str,
    db: Session = Depends(get_db_session),
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    return get_strategy_service.get_strategy_detail(strategy_id, db=db)


@strategy_router.post("/strategies")
@inject
def create_strategies(
    strategy_create: StrategyCreate,
    create_strategy_service: CreateStrategyUseCase = Depends(
        dependency=Provide[Container.create_strategy_service]
    ),
    db: Session = Depends(get_db_session),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    result = create_strategy_service.create_strategy_object(
        strategy_create, user, db=db
    )
    return result


@strategy_router.delete(
    "/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db_session),
    delete_strategy_service: DeleteStrategyUseCase = Depends(
        Provide[Container.delete_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    delete_strategy_service.exec(strategy_id, db=db)


@strategy_router.put("/strategies/{strategy_id}")
@inject
def update_strategy(
    strategy_id: str,
    strategy_update: StrategyCreate,
    db: Session = Depends(get_db_session),
    update_strategy_service: UpdateStrategyUseCase = Depends(
        Provide[Container.update_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    update_strategy_service.exec(strategy_id, strategy_update, user, db=db)


@strategy_router.post("/themes/preview")
@inject
def get_preview(
    preview_message_create: PreviewMessageCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
) -> PreviewMessageResponse:

    # recsys_model_id = preview_message_create.recsys_model_id  # recsys_model_id
    # audience_id = preview_message_create.theme_audience_set.audience_ids[
    #     0
    # ]  # audience_id
    # offer_ids_input = preview_message_create.theme_audience_set.offer_ids  # offer_id
    # if offer_ids_input is None:
    #     offer_id = []
    # elif len(offer_ids_input) == 0:
    #     offer_id = []
    # else:
    #     offer_id = offer_ids_input[0]

    # contents_tag = preview_message_create.theme_audience_set.contents_tags
    # if contents_tag is None:
    #     contents_id = []
    #     contents_name = []
    # elif len(contents_tag) == 0:
    #     contents_id = []
    #     contents_name = []
    # else:
    #     contents_id = contents_tag[0]
    #     contents_name = ""

    # contents_name
    # group_stats - item_ratio
    # group_stats - it_gb_ratio

    ##rep_nm
    ##set_group_category
    ##media
    ##msg_type

    ##input_data

    ## data_dict

    ##

    lms = PreviewMessage(
        msg_title="Sample Title",
        msg_body="This is a sample message body.",
        bottom_text="Bottom text",
        msg_announcement="Announcement text",
        msg_photo_uri=None,
        msg_send_type="campaign",
        media=CampaignMedia.TEXT_MESSAGE,
        msg_type=MessageType.LMS,
        kakao_button_links=None,
        phone_callback="123-456-7890",
    )

    kakao = PreviewMessage(
        msg_title="Kakao Sample Message",
        msg_body="KAKAO! KAKAO! KAKAO! KAKAO!KAKAO!",
        bottom_text="Bottom text",
        msg_announcement="Announcement text",
        msg_photo_uri=None,
        msg_send_type="campaign",
        media=CampaignMedia.KAKAO_FRIEND_TALK,
        msg_type=MessageType.KAKAO_IMAGE_GENERAL,
        kakao_button_links=[
            KakaoButtonLink(
                button_name="AICE",
                button_type=KakaoButtonType.WEB_LINK_BUTTON,
                web_link="https://aice-dev.foreket.ai",
            ),
            KakaoButtonLink(
                button_name="GOOGLE",
                button_type=KakaoButtonType.WEB_LINK_BUTTON,
                web_link="https://www.google.com",
            ),
        ],
        phone_callback="123-456-7890",
    )

    return PreviewMessageResponse(lms=lms, kakao_image_general=kakao)
