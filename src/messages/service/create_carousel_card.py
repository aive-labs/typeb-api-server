from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.admin.service.port.base_admin_repository import BaseAdminRepository
from src.campaign.routes.port.upload_image_for_message_usecase import (
    UploadImageForMessageUseCase,
)
from src.common.utils.get_env_variable import get_env_variable
from src.common.utils.validate_url import validate_url
from src.core.exceptions.exceptions import PolicyException
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.messages.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.messages.routes.port.create_carousel_card_usecase import (
    CreateCarouselCardUseCase,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.users.domain.user import User


class CreateCarouselCard(CreateCarouselCardUseCase):
    max_card_count = 6

    def __init__(
        self,
        message_repository: BaseMessageRepository,
        upload_image_for_message: UploadImageForMessageUseCase,
        admin_repository: BaseAdminRepository,
    ):
        self.message_repository = message_repository
        self.upload_image_for_message = upload_image_for_message
        self.admin_repository = admin_repository
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

    async def create_carousel_card(
        self,
        file: UploadFile,
        carousel_card_request: KakaoCarouselCardRequest,
        user: User,
        db: Session,
    ) -> KakaoCarouselCardResponse:

        personal_variable_response = self.admin_repository.get_personal_variables(user, db)
        personal_variables = [
            personal_variable.variable_symbol for personal_variable in personal_variable_response
        ]

        self.validate_image_url(carousel_card_request)
        self.validate_button_url(carousel_card_request, personal_variables)
        self.validate_carousel_message(carousel_card_request)
        self.validate_carousel_button_message(carousel_card_request)
        self.validate_carousel_card_count(carousel_card_request, db)
        self.validate_carousel_button_count(carousel_card_request)
        self.add_carousel_sort_num(carousel_card_request, db)

        if file:
            # 신규 캐러셀 카드 등록 또는 캐러셀 이미지 업데이트
            carousel_card = await self.create_carousel_card_with_image_link(
                carousel_card_request, db, file, user
            )
        else:
            # 캐러셀 문구만 업데이트(이미지는 업데이트 하지 않음)
            # id가 반드시 있어야 하는 단계
            if carousel_card_request.id is None:
                raise PolicyException(detail={"message": "업데이트 요청 중 문제가 발생했습니다."})
            prev_carousel = self.message_repository.get_carousel_card_by_id(
                carousel_card_request.id, db
            )
            carousel_card = KakaoCarouselCard(**carousel_card_request.model_dump())
            carousel_card.set_image_url(carousel_card.image_url, prev_carousel.s3_image_path)

        saved_carousel_card = self.message_repository.save_carousel_card(carousel_card, user, db)
        response = self.carousel_card_to_response(saved_carousel_card)

        db.commit()

        return response

    def validate_image_url(self, carousel_card_request: KakaoCarouselCardRequest):
        if not validate_url(carousel_card_request.image_link):
            raise PolicyException(detail={"message": "이미지 링크 형식이 올바르지 않습니다."})

    def validate_button_url(
        self, carousel_card_request: KakaoCarouselCardRequest, personal_variables: list[str]
    ):
        for button in carousel_card_request.carousel_button_links:
            if not validate_url(button.url_mobile):
                if button.url_mobile not in personal_variables:
                    raise PolicyException(
                        detail={"message": "버튼 링크(모바일) 형식이 올바르지 않습니다."}
                    )

            if button.url_pc:
                if not validate_url(button.url_pc):
                    if button.url_pc not in personal_variables:
                        raise PolicyException(
                            detail={"message": "버튼 링크(웹) 형식이 올바르지 않습니다."}
                        )

    def add_carousel_sort_num(self, carousel_card_request, db):
        if carousel_card_request.carousel_sort_num is None:
            max_sort_num = self.message_repository.get_max_carousel_sort_num(
                carousel_card_request.set_group_msg_seq, db
            )
            carousel_card_request.set_carousel_sort_num(max_sort_num)

    def validate_carousel_button_message(self, carousel_card_request):
        if carousel_card_request.carousel_button_links:
            for button in carousel_card_request.carousel_button_links:
                if len(button.name) > 28:
                    raise PolicyException(
                        detail={"message": "버튼 제목은 최대 28자까지 입력할 수 있습니다."}
                    )

    def validate_carousel_message(self, carousel_card_request):
        if len(carousel_card_request.message_title) > 20:
            raise PolicyException(
                detail={"message": "캐러셀 아이템 제목은 최대 20자까지 입력할 수 있습니다."}
            )
        if (
            carousel_card_request.message_body is not None
            and len(carousel_card_request.message_body) > 180
        ):
            raise PolicyException(
                detail={"message": "캐러셀 아이템 메시지는 최대 180자까지 입력할 수 있습니다."}
            )

    def carousel_card_to_response(self, saved_carousel_card):
        response = KakaoCarouselCardResponse(**saved_carousel_card.model_dump())
        response.set_image_url(f"{self.cloud_front_url}/{response.s3_image_path}")
        return response

    async def create_carousel_card_with_image_link(self, carousel_card_request, db, file, user):
        carousel_card = KakaoCarouselCard(**carousel_card_request.model_dump())

        carousel_image_links = await self.upload_image_for_message.upload_for_carousel(
            file, carousel_card, user, db
        )
        carousel_card.set_image_url(
            carousel_image_links.kakao_image_link, carousel_image_links.s3_image_path
        )
        return carousel_card

    def validate_carousel_button_count(self, carousel_card_request):
        if len(carousel_card_request.carousel_button_links) > 2:
            raise PolicyException(
                detail={"message": "캐러셀 아이템의 버튼은 최대 2개까지 등록이 가능합니다."}
            )

    def validate_carousel_card_count(self, carousel_card_request, db: Session):
        registered_card_count = self.message_repository.get_carousel_card_count(
            carousel_card_request.set_group_msg_seq, db
        )
        if carousel_card_request.id is None:
            if registered_card_count == 6:
                raise PolicyException(
                    detail={"message": "캐러셀 아이템은 최대 6장까지 등록이 가능합니다."}
                )
