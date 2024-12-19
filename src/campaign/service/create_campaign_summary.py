from sqlalchemy.orm import Session

from src.campaign.routes.dto.response.campaign_summary_response import (
    CampaignSummaryResponse,
)
from src.campaign.routes.port.create_campaign_summary_usecase import (
    CreateCampaignSummaryUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.utils.data_converter import DataConverter
from src.content.service.port.base_contents_repository import BaseContentsRepository
from src.main.exceptions.exceptions import ConsistencyException


class CreateCampaignSummary(CreateCampaignSummaryUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        contents_repository: BaseContentsRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.contents_repository = contents_repository

    def create_campaign_summary(self, campaign_id: str, db: Session) -> CampaignSummaryResponse:
        summary_campaign_query = self.campaign_set_repository.get_campaign_info_for_summary(
            campaign_id, db
        )
        summary_df = DataConverter.convert_query_to_df(summary_campaign_query)

        campaign_base = summary_df.iloc[0]

        campaign_type_code = campaign_base["campaign_type_code"]
        campaign_type_name = campaign_base["campaign_type_name"]
        campaign_status_code = campaign_base["campaign_status_code"]
        campaign_status_name = campaign_base["campaign_status_name"]
        send_type_code = campaign_base["send_type_code"]
        send_type_name = campaign_base["send_type_name"]
        repeat_type = campaign_base["repeat_type"]
        week_days = campaign_base["week_days"]
        start_date = campaign_base["start_date"]
        end_date = campaign_base["end_date"]
        send_date = campaign_base["send_date"]
        timetosend = campaign_base["timetosend"]
        audience_count = int(summary_df["audience_id"].nunique())

        total_reciepient = summary_df["recipient_group_count"].sum()
        budget = int(summary_df[["set_seq", "media_cost"]].drop_duplicates()["media_cost"].sum())

        # 발송 메세지 타입
        set_group_msg = self.campaign_set_repository.get_campaign_set_group_messages_in_use(
            campaign_id, db
        )

        set_group_seqs = []
        used_msg_type = []
        message_tup_lst = []
        campaign_msg_resv_date = None
        remind_step1_resv_date = None
        remind_step2_resv_date = None
        remind_step3_resv_date = None

        for mt in set_group_msg:
            set_group_seqs.append(mt.set_group_seq)
            used_msg_type.append(mt.msg_type)
            msg_tup = (mt.msg_send_type, mt.remind_step, mt.msg_resv_date)
            if msg_tup not in message_tup_lst:
                message_tup_lst.append(msg_tup)

                if mt.msg_resv_date is None:
                    raise ConsistencyException(
                        detail={"message": "예약날짜 값이 비어있습니다. 확인이 필요합니다."}
                    )

                resv_date: str = (
                    mt.msg_resv_date[0:4]
                    + "-"
                    + mt.msg_resv_date[4:6]
                    + "-"
                    + mt.msg_resv_date[6:]
                    + " "
                    + timetosend
                )

                if msg_tup[0] == "campaign":
                    campaign_msg_resv_date = resv_date
                elif msg_tup[0] == "remind":
                    if msg_tup[1] == 1:
                        remind_step1_resv_date = resv_date
                    elif msg_tup[1] == 2:
                        remind_step2_resv_date = resv_date
                    elif msg_tup[1] == 3:
                        remind_step3_resv_date = resv_date
                else:
                    raise ConsistencyException(
                        detail={"message": "예약날짜 값이 비어있습니다. 확인이 필요합니다."}
                    )

        msg_type_tup = list(set(used_msg_type))
        msg_type_count = len(msg_type_tup)

        contents_count = self.contents_repository.count_contents_by_campaign_id(
            campaign_id, set_group_seqs, db
        )

        res = CampaignSummaryResponse(
            campaign_type_code=campaign_type_code,
            campaign_type_name=campaign_type_name,
            send_type_code=send_type_code,
            send_type_name=send_type_name,
            total_reciepient=total_reciepient,
            budget=budget,
            repeat_type=repeat_type,
            week_days=week_days,
            start_date=start_date,
            end_date=end_date,
            send_date=send_date,
            campaign_status_code=campaign_status_code,
            campaign_status_name=campaign_status_name,
            msg_type_count=msg_type_count,
            msg_type_tup=msg_type_tup,
            audience_count=audience_count,
            contents_count=contents_count,
            campaign_msg_resv_date=campaign_msg_resv_date,
            remind_step1_resv_date=remind_step1_resv_date,
            remind_step2_resv_date=remind_step2_resv_date,
            remind_step3_resv_date=remind_step3_resv_date,
        )

        return res
