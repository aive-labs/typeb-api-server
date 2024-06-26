from fastapi import HTTPException

from src.audiences.enums.audience_type import AudienceType
from src.audiences.routes.port.usecase.delete_audience_usecase import (
    DeleteAudienceUsecase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.campaign.enums.campagin_status import CampaignStatus


class DeleteAudienceService(DeleteAudienceUsecase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def delete_audience(self, audience_id: str):
        """타겟 오디언스 삭제 함수

        -연결된 캠페인이 존재하는 경우
            - 연결 캠페인이 모두 기간만료 상태인 경우 -> 미표시 상태 update
            - 그 외의 경우 -> 삭제 불가. error raise
        """

        audience = self.audience_repository.get_audience(audience_id)

        if audience.audience_type_code == AudienceType.segment.value:
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "delete/02",
                    "message": "삭제 불가 - 세그먼트 타겟입니다.",
                },
            )

        linked_campaigns = self.audience_repository.get_linked_campaigns(audience_id)
        if len(linked_campaigns) >= 1:
            linked_camp_list = [row.campaign_status_code for row in linked_campaigns]

            # 캠페인이 1개이고 해당 캠페인의 상태가 expired 인 경우
            if self._is_single_expired_campaign(linked_camp_list):
                self.audience_repository.update_expired_audience_status(audience_id)

            raise HTTPException(
                status_code=500,
                detail={
                    "code": "delete/01",
                    "message": "삭제 불가 - 연결된 캠페인이 존재합니다.",
                },
            )

        self.audience_repository.delete_audience(audience_id)

    def _is_single_expired_campaign(self, campaign_list: list) -> bool:
        """
        캠페인 리스트에 단 하나의 캠페인이 있고, 그 상태가 'expired'인지 확인합니다.
        """
        return (
            len(campaign_list) == 1 and campaign_list[0] == CampaignStatus.expired.value
        )
