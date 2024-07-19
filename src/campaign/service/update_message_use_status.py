from datetime import datetime

import pandas as pd

from src.campaign.routes.port.update_message_use_status_usecase import (
    UpdateMessageUseStatusUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.timezone_setting import selected_timezone
from src.core.exceptions.exceptions import NotFoundException, PolicyException
from src.core.transactional import transactional


class UpdateMessageUseStatus(UpdateMessageUseStatusUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def exec(self, campaign_id, set_group_msg_seq, is_used_obj, user, db):
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
        if not campaign:
            raise NotFoundException(
                detail={"message": "메시지가 속한 캠페인 정보를 찾지 못했습니다."}
            )

        campaign_set_group_message = (
            self.campaign_set_repository.get_campaign_set_group_message_by_msg_seq(
                campaign_id, set_group_msg_seq, db
            )
        )
        old_message_used = campaign_set_group_message.is_used

        if campaign.campaign_status_code == "r2":
            # 발송된 메세지 수정 불가
            self.check_already_send_message(campaign_id, db, set_group_msg_seq)

            # 예약 날짜 입력 확인
            self.check_reservation_date(campaign_set_group_message)

            # 발송 예약시간 지난 메시지 확인
            self.check_reservation_time_expiry(
                campaign, campaign_set_group_message, is_used_obj, old_message_used
            )

        self.campaign_set_repository.update_use_status(
            campaign_id, set_group_msg_seq, is_used_obj.is_used, db
        )

    def check_reservation_time_expiry(
        self, campaign, campaign_set_group_message, is_used_obj, old_message_used
    ):
        message_reservation_date = campaign_set_group_message.msg_resv_date
        # 메시지 비활성화로 발송이 안된 메세지 : 기간이 지난 메세지는 다시 활성화 불가. 메세지 날짜를 확인해주세요
        if (old_message_used is False) and (is_used_obj.is_used is True):
            send_datetime_str = message_reservation_date + " " + campaign.timetosend
            send_datetime = pd.to_datetime(send_datetime_str, format="%Y%m%d %H:%M")
            current_datetime_str = datetime.now(selected_timezone).strftime("%Y%m%d %H:%M")
            if current_datetime_str > send_datetime:
                raise PolicyException(
                    detail={
                        "code": "message/update/denied",
                        "message": "발송예약시간이 지난 메세지는 다시 활성화할 수 없습니다.",
                    },
                )

    def check_reservation_date(self, campaign_set_group_message):
        message_reservation_date = campaign_set_group_message.msg_resv_date
        if message_reservation_date is None:
            raise PolicyException(
                detail={
                    "code": "message/update/denied",
                    "message": "예약날짜가 입력되어 있지 않습니다.",
                },
            )
        return message_reservation_date

    def check_already_send_message(self, campaign_id, db, set_group_msg_seq):
        send_message = self.campaign_repository.get_message_in_send_reservation(
            campaign_id, set_group_msg_seq, db
        )
        if send_message:
            raise PolicyException(
                detail={
                    "code": "message/update/denied",
                    "message": "이미 발송된 메세지는 수정이 불가합니다.",
                },
            )
