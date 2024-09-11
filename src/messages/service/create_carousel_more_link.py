from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.domain.kakao_carousel_more_link import KakaoCarouselMoreLink
from src.messages.routes.dto.request.kakao_carousel_more_link_request import (
    KakaoCarouselMoreLinkRequest,
)
from src.messages.routes.port.create_carousel_more_link_usecase import (
    CreateCarouselMoreLinkUseCase,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.users.domain.user import User


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
        carousel_more_link = KakaoCarouselMoreLink(
            set_group_msg_seq=set_group_msg_seq,
            url_pc=carousel_more_link_request.url_pc,
            url_mobile=carousel_more_link_request.url_mobile,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

        self.message_repository.save_carousel_more_link(carousel_more_link, user, db)
