import logging
from datetime import datetime

import pytz
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.get_campaign_base_obj import (
    get_campaign_base_obj,
)
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.routes.port.reserve_campaigns_usecase import ReserveCampaignsUseCase
from src.campaign.service.campaign_manager import CampaignManager
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import (
    create_logical_date_for_airflow,
    get_current_datetime_yyyymmddhh24mi,
)
from src.core.exceptions.exceptions import NotFoundException
from src.messages.service.message_reserve_controller import MessageReserveController
from src.users.domain.user import User


class ReserveCampaignsService(ReserveCampaignsUseCase):

    def __init__(self, approve_campaign_service: ApproveCampaignUseCase):
        self.approve_campaign_service = approve_campaign_service
        self.message_controller = MessageReserveController()

    async def reserve_campaigns(self, campaign_id, execution_date, user: User, db: Session) -> dict:
        """
        campaign_id -> (운영중 상태) & (당일 발송할 메세지가 있는) 캠페인

        execution_date - > execution_date(airflow): (당일)

        daily 실행되는 API
        - 예약이 필요한 메세지 유무 체크
        - recipients 업데이트
        - offer_cust 데이터 인서트 & dag trigger (campaign 메세지인 경우에만 한번 저장)
        - 발송예약 데이터 인서트
        - nepa_send insert dag trigger
        """

        campaign_base_obj = get_campaign_base_obj(db, campaign_id)

        if not campaign_base_obj:
            raise NotFoundException(
                detail={"message": f"캠페인({campaign_id})이 존재하지 않습니다."}
            )

        campaign_base_dict = DataConverter.convert_model_to_dict(campaign_base_obj)
        print(f"campaign_base_dict: {campaign_base_dict}")
        send_date = campaign_base_dict["send_date"]
        send_time = campaign_base_dict["timetosend"]
        shop_send_yn = campaign_base_dict["shop_send_yn"]

        # logging
        tz = "Asia/Seoul"
        korea_timezone = pytz.timezone(tz)
        curren_time = datetime.now(korea_timezone)
        current_date = curren_time.strftime("%Y%m%d")

        log_file_path = f"./logs/send_reserv_log_{current_date}.logs"

        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )
        logging.info(f"[dag-reservation] campaign_id: {campaign_id} 예약일({execution_date})")

        # 당일 예약이 필요한 메세지 가져오기
        set_group_msg_obj = (
            db.query(SetGroupMessagesEntity.set_group_msg_seq)
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.msg_resv_date == execution_date,
            )
            .distinct()
        )

        set_group_msgs = [msg[0] for msg in set_group_msg_obj]

        if len(set_group_msgs) == 0:
            txt = f"{campaign_id} : 당일({execution_date}) 발송될 메세지가 존재하지 않습니다."
            logging.info(txt)
            return {"result": txt}

        # 예약된 메세지 가져오기
        reserved_msg_obj = (
            db.query(SendReservationEntity.set_group_msg_seq)
            .filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
            )
            .distinct()
        )
        reserved_msg_seqs = [msg[0] for msg in reserved_msg_obj]

        # 당일 발송되어야하는데 예약이 아직 안된 메세지 가져오기
        msg_seqs_to_save = [
            msg_seq for msg_seq in set_group_msgs if msg_seq not in reserved_msg_seqs
        ]

        if len(msg_seqs_to_save) == 0:
            txt = f"{campaign_id} : 당일({execution_date})까지 발송될 메세지를 모두 예약하였습니다."
            logging.info(txt)
            return {"result": txt}

        # recipient 업데이트
        recipient_count = (
            db.query(CampaignSetRecipientsEntity)
            .filter(CampaignSetRecipientsEntity.campaign_id == campaign_id)
            .count()
        )

        logging.info(f"[dag-reservation] 현재 recipient_count: {recipient_count}명")
        print(f"현재 recipient_count: {recipient_count}명")
        campaign_manager = CampaignManager(db, shop_send_yn, user.user_id)
        recipient_df = campaign_manager.prepare_campaign_recipients(campaign_base_dict)
        if recipient_df is not None:
            campaign_manager.update_campaign_recipients(recipient_df)

        print(f"변경 후: {len(recipient_df)}명")
        logging.info(f"[dag-reservation] 변경 후: {len(recipient_df)}명")
        db.commit()

        # insert to send_reservation : 이미 예약한 메세지를 제외하고 예약하기
        res = self.approve_campaign_service.save_campaign_reservation(
            db, user, campaign_id, msg_seqs_to_save
        )

        if res:
            # airflow trigger api
            print("today airflow trigger api")
            input_var = {
                "mallid": user.mall_id,
                "campaign_id": campaign_id,
                "test_send_yn": "n",
            }
            yyyymmddhh24mi = get_current_datetime_yyyymmddhh24mi()
            dag_run_id = f"{campaign_id}_{str(yyyymmddhh24mi)}"
            print(f"dag_run_id: {dag_run_id} / input_var: {input_var}")
            logical_date = create_logical_date_for_airflow(send_date, send_time)

            await self.message_controller.execute_dag(
                dag_name="send_messages",
                input_vars=input_var,
                dag_run_id=dag_run_id,
                logical_date=logical_date,
            )

            await self.message_controller.execute_dag(
                dag_name=f"{user.mall_id}_issue_coupon",
                input_vars=input_var,
                dag_run_id=dag_run_id,
                logical_date=logical_date,
            )

        else:
            txt = f"{campaign_id} : 당일({execution_date}) 정상 예약 메세지가 존재하지 않습니다."
            return {"result": txt}

        return {"result": "success"}
