from sqlalchemy.orm import Session

from src.campaign.routes.port.delete_image_for_message_usecase import (
    DeleteImageForMessageUseCase,
)
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.utils.file.s3_service import S3Service


class DeleteImageForMessage(DeleteImageForMessageUseCase):

    def __init__(
        self,
        campaign_set_repository: BaseCampaignSetRepository,
        s3_service: S3Service,
    ):
        self.campaign_set_repository = campaign_set_repository
        self.s3_service = s3_service

    async def exec(self, campaign_id: str, set_group_msg_seq, user, db: Session):
        message_resource = self.campaign_set_repository.get_message_image_source(
            set_group_msg_seq, db
        )

        s3_key = message_resource.img_uri if message_resource.img_uri else None
        if s3_key:
            await self.s3_service.delete_object_async(s3_key)

        self.campaign_set_repository.delete_message_image_source(set_group_msg_seq, db)
        self.campaign_set_repository.delete_msg_photo_uri_by_set_group_msg_req(
            set_group_msg_seq, db
        )
        db.commit()
