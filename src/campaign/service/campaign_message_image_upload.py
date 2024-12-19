from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.routes.port.campaign_message_image_upload_usecase import (
    CampaignMessageImageUploadUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.exceptions.exceptions import PolicyException
from src.core.transactional import transactional
from src.user.domain.user import User


class CampaignMessageImageUploadService(CampaignMessageImageUploadUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def exec(
        self, campaign_id, set_group_msg_seq, files: list[UploadFile], user: User, db: Session
    ):
        campaign = self.campaign_repository.get_campaign_detail(campaign_id)

        if campaign.campaign_status_code == "r2":
            # 발송된 메세지 수정 불가
            send_msg_first = (
                db.query(SendReservationEntity)
                .filter(
                    SendReservationEntity.campaign_id == campaign_id,
                    "n" == SendReservationEntity.test_send_yn,
                    SendReservationEntity.set_group_msg_seq == set_group_msg_seq,
                    SendReservationEntity.send_resv_state.not_in(
                        ["21", "01", "00"]
                    ),  # 발송한 메세지 필터
                )
                .first()
            )
            if send_msg_first:
                raise PolicyException(
                    detail={
                        "code": "message/update/denied",
                        "message": "이미 발송된 메세지는 수정이 불가합니다.",
                    }
                )

        set_group_message = self.campaign_set_repository.get_set_group_message(
            campaign_id, set_group_msg_seq, db
        )
        msg_type = set_group_message.msg_type
        old_message_image_url = set_group_message.msg_photo_uri

        # s3 파일 업로드
        # 뿌리오 파일 업로드
