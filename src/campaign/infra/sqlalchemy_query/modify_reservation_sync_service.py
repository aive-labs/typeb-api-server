from datetime import datetime, timedelta

from sqlalchemy import and_, delete

from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.service.campaign_manager import CampaignManager
from src.common.timezone_setting import selected_timezone
from src.common.utils import repeat_date
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter


class ModifyReservSync:
    def __init__(self, db, updated_by, campaign_id):
        self.db = db
        self.updated_by = updated_by
        self.campaign_id = campaign_id
        self.campaign_obj = (
            self.db.query(CampaignEntity)
            .filter(CampaignEntity.campaign_id == self.campaign_id)
            .first()
        )

    def delete_send_reservation_by_seq(self, set_group_msg_seqs):
        stmt = delete(SendReservationEntity).where(
            and_(
                SendReservationEntity.campaign_id == self.campaign_id,
                SendReservationEntity.send_resv_state == "21",  # 취소된 메세지
                SendReservationEntity.set_group_msg_seq.in_(set_group_msg_seqs),
            )
        )
        self.db.execute(stmt)
        self.db.flush()

    def delete_send_reservation_by_campaign(self):
        stmt = delete(SendReservationEntity).where(
            and_(
                SendReservationEntity.campaign_id == self.campaign_id,
                SendReservationEntity.send_resv_state == "21",  # 취소된 메세지
            )
        )
        self.db.execute(stmt)
        self.db.flush()

    def find_recurring_campaigns(self):
        # “운영중”, “기간만료”, “완료” 상태가 아닌 참조하는 캠페인(new)만 찾는 함수
        recurr_campaigns = (
            self.db.query(CampaignEntity)
            .filter(
                CampaignEntity.campaign_group_id == self.campaign_obj.campaign_group_id,
                CampaignEntity.start_date > self.campaign_obj.start_date,
                CampaignEntity.campaign_status_code.not_in(["o1", "o2", "s2"]),
            )
            .order_by(CampaignEntity.start_date)
        )

        return [camp.campaign_id for camp in recurr_campaigns]

    def get_recurring_date_update(self, bef_campaign_obj, campaign_base, changed_values):

        tz = "Asia/Seoul"

        # 직전 캠페인의 종료일
        create_date = datetime.strptime(bef_campaign_obj.end_date, "%Y%m%d")
        create_date = (
            create_date - timedelta(days=int(bef_campaign_obj.retention_day))
            if bef_campaign_obj.retention_day
            else create_date
        )
        org_campaign_end_date = selected_timezone.localize(create_date)

        # 종료일(end_date) - retention_day
        # 직전 캠페인 종료일 + 1day 가 start_date로 지정됨
        # 캠페인 생성일 != 캠페인 시작일
        start_date, end_date = repeat_date.calculate_dates(
            org_campaign_end_date,
            period=bef_campaign_obj.repeat_type,
            week_days=bef_campaign_obj.week_days,
            datetosend=(
                int(bef_campaign_obj.datetosend) if bef_campaign_obj.datetosend else None
            ),  # Null or datetosend
            timezone=tz,  # timezone
        )

        if bef_campaign_obj.retention_day:
            end_date_f = datetime.strptime(end_date, "%Y%m%d")
            end_date = end_date_f + timedelta(days=int(bef_campaign_obj.retention_day))
            end_date = end_date.strftime("%Y%m%d")

        campaign_base.start_date = start_date
        campaign_base.end_date = end_date
        campaign_base.send_date = start_date
        campaign_base.datetosend = bef_campaign_obj.datetosend
        campaign_base.repeat_type = bef_campaign_obj.repeat_type
        campaign_base.timetosend = bef_campaign_obj.timetosend
        campaign_base.week_days = bef_campaign_obj.week_days
        campaign_base.group_end_date = bef_campaign_obj.group_end_date
        campaign_base.is_approval_recurred = bef_campaign_obj.is_approval_recurred
        campaign_base.is_msg_creation_recurred = bef_campaign_obj.is_msg_creation_recurred
        campaign_base.campaign_status_code = "r2"  # 리마인드 수정을 위해 상태를 "수정단계로" 변경

        # 발송일이 변경되면 메시지 오브젝트도 변경
        if "send_date" in changed_values:
            set_group_msg_obj = (
                self.db.query(SetGroupMessagesEntity)
                .filter(SetGroupMessagesEntity.campaign_id == campaign_base.campaign_id)
                .all()
            )
            for msg_obj in set_group_msg_obj:
                if msg_obj.msg_send_type == "campaign":
                    msg_obj.msg_resv_date = start_date
                    msg_obj.updated_by = str(self.updated_by)
                    msg_obj.updated_at = localtime_converter()

        self.db.flush()
        return campaign_base

    def sync_recurring_campaign(self, bef_campaign_id, campaign_id, changed_values):

        campaign_base = (
            self.db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )
        if bef_campaign_id:
            bef_campaign_obj = (
                self.db.query(CampaignEntity)
                .filter(CampaignEntity.campaign_id == bef_campaign_id)
                .first()
            )
            return self.get_recurring_date_update(bef_campaign_obj, campaign_base, changed_values)
        else:
            return self.get_recurring_date_update(self.campaign_obj, campaign_base, changed_values)

    def get_reserve_msgs(self, current_korea_date):

        campaign_base_dict = DataConverter.convert_model_to_dict(self.campaign_obj)
        shop_send_yn = campaign_base_dict["shop_send_yn"]

        # to-do: 발송예약시간이 지난 메세지 제외하기

        # 당일 예약이 필요한 메세지 가져오기
        print(f"{current_korea_date} current_korea_date")
        set_group_msg_obj = (
            self.db.query(SetGroupMessagesEntity.set_group_msg_seq)
            .filter(
                SetGroupMessagesEntity.campaign_id == self.campaign_id,
                SetGroupMessagesEntity.msg_resv_date == current_korea_date,
            )
            .distinct()
        )

        set_group_msgs = [msg[0] for msg in set_group_msg_obj]

        if len(set_group_msgs) == 0:
            txt = f"{self.campaign_id} : 당일({current_korea_date}) 발송될 메세지가 존재하지 않습니다."
            return {"result": txt}

        # 예약된 메세지 가져오기
        reserved_msg_obj = (
            self.db.query(SendReservationEntity.set_group_msg_seq)
            .filter(
                SendReservationEntity.campaign_id == self.campaign_id,
                SendReservationEntity.test_send_yn == "n",
                SendReservationEntity.send_resv_state.not_in(["21", "01", "00"]),
            )
            .distinct()
        )
        reserved_msg_seqs = [msg[0] for msg in reserved_msg_obj]

        # 당일 발송되어야하는데 예약이 아직 안된 메세지 가져오기
        # daily 예약
        # 발송된 메세지를 제외하고, 추가된 메세지 & 수정된 메세지를 다시 예약한다.
        msg_seqs_to_save = [
            msg_seq for msg_seq in set_group_msgs if msg_seq not in reserved_msg_seqs
        ]

        if len(msg_seqs_to_save) == 0:
            txt = f"{self.campaign_id} : 당일({current_korea_date})까지 발송될 메세지를 모두 예약하였습니다."
            return {"result": txt}

        # recipient 업데이트
        recipient_count = (
            self.db.query(CampaignSetRecipientsEntity)
            .filter(CampaignSetRecipientsEntity.campaign_id == self.campaign_id)
            .count()
        )

        print(f"현재 recipient_count: {recipient_count}명")
        campaign_manager = CampaignManager(self.db, shop_send_yn, self.updated_by)
        recipient_df = campaign_manager.prepare_campaign_recipients(campaign_base_dict)
        if recipient_df is not None:
            campaign_manager.update_campaign_recipients(recipient_df)

        print(f"변경 후: {len(recipient_df)}명")

        return msg_seqs_to_save
