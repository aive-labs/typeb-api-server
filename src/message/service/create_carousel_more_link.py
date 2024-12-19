from sqlalchemy.orm import Session

from src.common.utils.validate_url import validate_url
from src.main.exceptions.exceptions import PolicyException
from src.main.transactional import transactional
from src.message.domain.kakao_carousel_more_link import KakaoCarouselMoreLink
from src.message.routes.dto.request.kakao_carousel_more_link_request import (
    KakaoCarouselMoreLinkRequest,
)
from src.message.routes.port.create_carousel_more_link_usecase import (
    CreateCarouselMoreLinkUseCase,
)
from src.message.service.port.base_message_repository import BaseMessageRepository
from src.user.domain.user import User


class CreateCarouselMoreLink(CreateCarouselMoreLinkUseCase):

    def __init__(self, message_repository: BaseMessageRepository):
        self.message_repository = message_repository

    @transactional
    def exec(
        self,
        set_group_msg_seq: int,
        carousel_more_link_request: KakaoCarouselMoreLinkRequest,
        user: User,
        db: Session,
    ):

        more_link_id = self.message_repository.get_carousel_more_link_id_by_set_group_msg_seq(
            set_group_msg_seq, db
        )
        carousel_more_link = KakaoCarouselMoreLink(
            id=more_link_id,
            set_group_msg_seq=set_group_msg_seq,
            url_pc=carousel_more_link_request.url_pc,
            url_mobile=carousel_more_link_request.url_mobile,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

        self.message_repository.save_carousel_more_link(carousel_more_link, db)

    def validate_button_url(self, carousel_more_link_request: KakaoCarouselMoreLinkRequest):
        if not validate_url(carousel_more_link_request.url_mobile):
            raise PolicyException(detail={"message": "버튼 링크(모바일) 형식이 올바르지 않습니다."})

        if carousel_more_link_request.url_pc:
            if not validate_url(carousel_more_link_request.url_pc):
                raise PolicyException(detail={"message": "버튼 링크(웹) 형식이 올바르지 않습니다."})
