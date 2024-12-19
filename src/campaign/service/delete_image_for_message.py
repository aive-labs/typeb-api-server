from sqlalchemy.orm import Session

from src.campaign.domain.campaign_messages import Message
from src.campaign.routes.dto.response.set_group_seq_with_message_response import (
    SetGroupSeqWithMessageResponse,
)
from src.campaign.routes.port.delete_image_for_message_usecase import (
    DeleteImageForMessageUseCase,
)
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.utils.file.s3_service import S3Service
from src.main.exceptions.exceptions import ConsistencyException
from src.message_template.enums.message_type import MessageType


class DeleteImageForMessage(DeleteImageForMessageUseCase):

    def __init__(
        self,
        campaign_set_repository: BaseCampaignSetRepository,
        s3_service: S3Service,
    ):
        self.campaign_set_repository = campaign_set_repository
        self.s3_service = s3_service

    async def exec(
        self, campaign_id: str, set_group_msg_seq, user, db: Session
    ) -> SetGroupSeqWithMessageResponse:
        message_resource = self.campaign_set_repository.get_message_image_source(
            set_group_msg_seq, db
        )

        # s3 이미지 삭제
        s3_key = message_resource.img_uri if message_resource.img_uri else None
        if s3_key:
            await self.s3_service.delete_object_async(s3_key)

        # DB 데이터 삭제
        self.campaign_set_repository.delete_message_image_source(set_group_msg_seq, db)
        self.campaign_set_repository.delete_msg_photo_uri_by_set_group_msg_req(
            set_group_msg_seq, db
        )

        set_group_message = self.campaign_set_repository.get_campaign_set_group_message_by_msg_seq(
            campaign_id, set_group_msg_seq, db
        )
        msg_type = set_group_message.msg_type
        if not msg_type:
            raise ConsistencyException(
                detail={"message": "메시지 타입 값이 존재하지 않습니다. 관리자에게 문의해주세요."}
            )
        # 메시지 타입 업데이트
        if msg_type == MessageType.MMS.value:
            body = set_group_message.msg_body if set_group_message.msg_body else ""
            bottom_text = set_group_message.bottom_text if set_group_message.bottom_text else ""
            if len(body) + len(bottom_text) < 45:
                msg_type_update = "sms"
            else:
                msg_type_update = "lms"
        elif msg_type in (
            MessageType.KAKAO_IMAGE_GENERAL.value,
            MessageType.KAKAO_IMAGE_WIDE.value,
        ):
            msg_type_update = "kakao_text"
        else:
            raise ConsistencyException(detail={"message": "지원되지 않는 메시지 타입입니다."})

        if msg_type_update:
            self.campaign_set_repository.update_campaign_set_group_message_type(
                campaign_id, set_group_message, msg_type_update, db
            )

        updated_set_group_message = (
            self.campaign_set_repository.get_campaign_set_group_message_by_msg_seq(
                campaign_id, set_group_msg_seq, db
            )
        )

        updated_message = Message.from_set_group_message(updated_set_group_message)

        db.commit()

        return SetGroupSeqWithMessageResponse(
            set_group_msg_seq=set_group_msg_seq, msg_obj=updated_message
        )
