from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.infra.entity.kakao_carousel_card_entity import KakaoCarouselCardEntity
from src.messages.infra.entity.kakao_carousel_link_button_entity import (
    KakaoCarouselLinkButtonsEntity,
)
from src.messages.infra.entity.ppurio_message_result_entity import (
    PpurioMessageResultEntity,
)
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.users.domain.user import User


class MessageRepository(BaseMessageRepository):

    def save_message_result(self, result: PpurioMessageResult, db: Session):
        new_entity = ModelConverter.model_to_entity(result, PpurioMessageResultEntity)
        db.add(new_entity)

    def save_carousel_card(
        self, carousel_card: KakaoCarouselCardRequest, user: User, db: Session
    ) -> KakaoCarouselCard:
        # 버튼 링크 엔티티 리스트를 생성
        button_entities = [
            KakaoCarouselLinkButtonsEntity(
                name=button.name,
                type=button.type,
                url_pc=button.url_pc,
                url_mobile=button.url_mobile,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )
            for button in carousel_card.carousel_button_links
        ]

        # KakaoCarouselCardEntity 생성 시 버튼 엔티티들을 함께 설정
        carousel_card_entity = KakaoCarouselCardEntity(
            carousel_sort_num=carousel_card.carousel_sort_num,
            message_title=carousel_card.message_title,
            message_body=carousel_card.message_body,
            image_url=carousel_card.image_url,
            image_title=carousel_card.image_title,
            image_link=carousel_card.image_link,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
            carousel_button_links=button_entities,
        )

        # 부모 엔티티와 자식 엔티티를 동시에 세션에 추가
        db.add(carousel_card_entity)
        db.flush()

        return KakaoCarouselCard.model_validate(carousel_card_entity)

    def delete_carousel_card(self, carousel_card_id: int, db: Session):
        db.query(KakaoCarouselCardEntity).filter_by(
            KakaoCarouselCardEntity.id == carousel_card_id
        ).delete()
