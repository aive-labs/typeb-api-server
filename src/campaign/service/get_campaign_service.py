from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
    StatusUserProfile,
)
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.users.domain.user import User


class GetCampaignService(GetCampaignUseCase):

    def __init__(self, campaign_repository: BaseCampaignRepository):
        self.campaign_repository = campaign_repository

    def get_campaigns(self, start_date: str, end_date: str, user: User) -> list[Campaign]:
        campaigns = self.campaign_repository.get_campaigns(start_date, end_date, user)
        return campaigns

    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimelineResponse]:
        campaign_timelines = self.campaign_repository.get_timeline(campaign_id, db)

        return [
            CampaignTimelineResponse(
                timeline_no=timeline.timeline_no,
                timeline_type=timeline.timeline_type,
                description=timeline.description,
                status_no=timeline.status_no,
                created_at=timeline.created_at,
                created_by=StatusUserProfile(
                    user_id=timeline.created_by,
                    username=timeline.created_by_name,
                    email=timeline.email,
                    photo_uri=timeline.photo_uri,
                    department_id=timeline.department_id,
                    department_name=timeline.department_name,
                    test_callback_number=timeline.test_callback_number,
                ),
            )
            for timeline in campaign_timelines
        ]
