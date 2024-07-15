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

    def get_campaign_detail(self, campaign_id, user, db: Session):
        # campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
        # campaign_reminds = self.campaign_repository.get_campaign_remind(campaign_id, db)

        # remind_list = [
        #     CampaignRemindResponse(
        #         remind_step=remind.remind_step,
        #         remind_media=remind.remind_media,
        #         remind_duration=remind.remind_duration,
        #     )
        #     for remind in campaign_reminds
        # ]

        # sets = [row._asdict() for row in get_campaign_sets(campaign_id=campaign_id, db=db)]
        # set_groups = [
        #     row._asdict() for row in get_campaign_set_groups(campaign_id=campaign_id, db=db)
        # ]

        # # rep_nm_list & contents_names
        # if campaign.campaign_type_code == CampaignType.expert.value:
        #     sets = add_set_rep_contents(db, sets, set_groups, campaign_id)
        # else:
        #     sets = [
        #         {**data_dict, "rep_nm_list": None, "contents_names": None} for data_dict in sets
        #     ]
        #
        # set_group_messages = get_campaign_set_group_messages(db, campaign_id=campaign_id)
        #
        # set_group_message_list = convert_to_set_group_message_list(set_group_messages)
        #
        # recipient_portion, total_cus, set_cus_count = get_set_portion(db, campaign_id)
        # set_df = pd.DataFrame(sets)
        #
        # if len(set_df) > 0:
        #     recipient_descriptions = set_summary_sententce(set_cus_count, set_df)
        # else:
        #     recipient_descriptions = None

        reviewer_list = self.campaign_repository.get_campaign_reviewers(campaign_id, db)
        for reviewer in reviewer_list:
            reviewer.user_name = "/".join([reviewer.user_name, reviewer.department_abb_name])
