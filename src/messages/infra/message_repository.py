from sqlalchemy import func
from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.core.exceptions.exceptions import NotFoundException
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.domain.kakao_carousel_more_link import KakaoCarouselMoreLink
from src.messages.infra.entity.kakao_carousel_card_entity import KakaoCarouselCardEntity
from src.messages.infra.entity.kakao_carousel_link_button_entity import (
    KakaoCarouselLinkButtonsEntity,
)
from src.messages.infra.entity.kakao_carousel_more_link_entity import (
    KakaoCarouselMoreLinkEntity,
)
from src.messages.infra.entity.ppurio_message_result_entity import (
    PpurioMessageResultEntity,
)
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.users.domain.user import User


class MessageRepository(BaseMessageRepository):

    def save_message_result(self, result: PpurioMessageResult, db: Session):
        new_entity = ModelConverter.model_to_entity(result, PpurioMessageResultEntity)
        db.add(new_entity)

    def save_carousel_card(
        self, carousel_card: KakaoCarouselCard, user: User, db: Session
    ) -> KakaoCarouselCard:
        # 버튼 링크 엔티티 리스트를 생성
        button_entities = [
            KakaoCarouselLinkButtonsEntity(
                id=button.id,
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
            id=carousel_card.id,
            set_group_msg_seq=carousel_card.set_group_msg_seq,
            carousel_sort_num=carousel_card.carousel_sort_num,
            message_title=carousel_card.message_title,
            message_body=carousel_card.message_body,
            image_url=carousel_card.image_url,
            image_title=carousel_card.image_title,
            image_link=carousel_card.image_link,
            s3_image_path=carousel_card.s3_image_path,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
            carousel_button_links=button_entities,
        )

        # 부모 엔티티와 자식 엔티티를 동시에 세션에 추가
        saved_carousel_card_entity = db.merge(carousel_card_entity)
        db.flush()

        return KakaoCarouselCard.model_validate(saved_carousel_card_entity)

    def delete_carousel_card(self, carousel_card_id: int, db: Session) -> int:
        db.query(KakaoCarouselLinkButtonsEntity).filter(
            KakaoCarouselLinkButtonsEntity.carousel_card_id == carousel_card_id
        ).delete()

        entity = (
            db.query(KakaoCarouselCardEntity)
            .filter(KakaoCarouselCardEntity.id == carousel_card_id)
            .first()
        )

        if entity is None:
            raise NotFoundException(detail={"message": "캐러셀이 존재하지 않습니다."})

        set_group_msg_seq = entity.set_group_msg_seq

        db.query(KakaoCarouselCardEntity).filter(
            KakaoCarouselCardEntity.id == carousel_card_id
        ).delete()

        db.flush()

        # 1. sort_num을 기준으로 모든 레코드를 오름차순으로 가져오기
        cards = (
            db.query(KakaoCarouselCardEntity)
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == set_group_msg_seq)
            .order_by(KakaoCarouselCardEntity.carousel_sort_num)
            .all()
        )

        # 2. 각 레코드의 carousel_sort_num을 1부터 차례대로 업데이트
        for idx, card in enumerate(cards, start=1):
            card.carousel_sort_num = idx

        db.flush()

        return set_group_msg_seq

    def save_carousel_more_link(self, carousel_more_link: KakaoCarouselMoreLink, db: Session):
        entity = KakaoCarouselMoreLinkEntity(
            id=carousel_more_link.id,
            set_group_msg_seq=carousel_more_link.set_group_msg_seq,
            url_pc=carousel_more_link.url_pc,
            url_mobile=carousel_more_link.url_mobile,
            created_by=carousel_more_link.created_by,
            updated_by=carousel_more_link.updated_by,
        )

        db.merge(entity)

    def get_carousel_card_count(self, set_group_msg_seq, db: Session) -> int:
        return (
            db.query(func.count(KakaoCarouselCardEntity.id))
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == set_group_msg_seq)
            .scalar()
        )

    def get_carousel_more_link_id_by_set_group_msg_seq(
        self, set_group_msg_seq, db: Session
    ) -> int | None:
        entity = (
            db.query(KakaoCarouselMoreLinkEntity)
            .filter(KakaoCarouselMoreLinkEntity.set_group_msg_seq == set_group_msg_seq)
            .first()
        )
        if entity is None:
            return None

        return entity.id

    def get_carousel_card_by_id(self, id, db) -> KakaoCarouselCard:
        entity = db.query(KakaoCarouselCardEntity).filter(KakaoCarouselCardEntity.id == id).first()
        if entity is None:
            raise NotFoundException(detail={"message": "캐러셀이 존재하지 않습니다."})

        return KakaoCarouselCard.model_validate(entity)

    def get_carousel_cards_by_set_group_msg_seq(
        self, set_group_msg_seq, db
    ) -> list[KakaoCarouselCard]:
        entities = (
            db.query(KakaoCarouselCardEntity)
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == set_group_msg_seq)
            .all()
        )
        return [KakaoCarouselCard.model_validate(entity) for entity in entities]

    def get_max_carousel_sort_num(self, set_group_msg_seq, db) -> int:
        entity = (
            db.query(KakaoCarouselCardEntity)
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == set_group_msg_seq)
            .first()
        )
        if entity is None:
            return 1

        max_sort_num = (
            db.query(func.max(KakaoCarouselCardEntity.carousel_sort_num))
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == set_group_msg_seq)
            .scalar()
        )

        return max_sort_num + 1

    def add_carousel_card_to_set_group_message(
        self, default_carousel_card: KakaoCarouselCard, db: Session
    ):
        entity = KakaoCarouselCardEntity(
            set_group_msg_seq=default_carousel_card.set_group_msg_seq,
            carousel_sort_num=default_carousel_card.carousel_sort_num,
            message_title=default_carousel_card.message_title,
            message_body=default_carousel_card.message_body,
            image_url="",
            image_title="",
            image_link="",
            s3_image_path="",
            created_at=default_carousel_card.created_at,
            created_by=default_carousel_card.created_by,
            updated_at=default_carousel_card.updated_at,
            updated_by=default_carousel_card.updated_by,
        )
        db.add(entity)
        db.flush()
