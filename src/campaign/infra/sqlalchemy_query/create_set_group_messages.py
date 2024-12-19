from sqlalchemy.orm import Session

from src.auth.infra.entity.message_integration_entity import MessageIntegrationEntity
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.get_campaign_remind import get_campaign_remind
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.date_utils import get_reservation_date
from src.main.exceptions.exceptions import PolicyException
from src.message_template.enums.message_type import MessageType


def create_set_group_messages(
    user_id,
    campaign_id,
    msg_delivery_vendor,
    start_date,
    send_date,
    has_remind,
    set_group_seqs,
    campaign_type_code,
    db: Session,
):
    """캠페인 그룹 메세지 시퀀스 생성 (set_group_msg_seq)

    *set_group_seq별 set_group_msg_seq를 미리 생성
    추후 step3 진입(메세지 생성) 시 set_group_msg_seq의 정보가 채워짐
      -msg_title
      -msg_body
      -msg_type
      -msg_send_type ..등

    추가 이슈:
    set_group_messages 테이블에 remind_req를 저장할 것인지?
    remind가 없는경우

    insert tables
    - set_group_messages
    """

    print("create message")
    print("set_group_seqs")
    print(set_group_seqs)

    message_sender_info_entity = db.query(MessageIntegrationEntity).first()
    if message_sender_info_entity is None:
        raise PolicyException(detail={"message": "입력된 발신자 정보가 없습니다."})
    bottom_text = f"무료수신거부: {message_sender_info_entity.opt_out_phone_number}"
    phone_callback = message_sender_info_entity.sender_phone_number

    # 기본 캠페인 -> (광고)[네파]
    # expert 캠페인 -> None
    if campaign_type_code == CampaignType.BASIC.value:
        msg_body = "메시지를 입력해주세요."
    else:
        msg_body = None

    if has_remind:
        remind_dict = [row._asdict() for row in get_campaign_remind(db, campaign_id)]
    else:
        remind_dict = None

    initial_msg_type = {
        CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
        CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
        CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
    }

    camp_resv_date = get_reservation_date(
        msg_send_type="campaign", start_date=start_date, send_date=send_date, remind_date=None
    )

    set_group_messages_all = []
    for set_group_dict in set_group_seqs:

        set_campaign_message_dict = set_group_dict
        set_campaign_message_dict["msg_body"] = (
            msg_body if set_group_dict["media"] != "kat" else None
        )
        set_campaign_message_dict["bottom_text"] = bottom_text
        set_campaign_message_dict["phone_callback"] = phone_callback
        set_campaign_message_dict["campaign_id"] = campaign_id
        set_campaign_message_dict["msg_send_type"] = "campaign"
        set_campaign_message_dict["is_used"] = True
        set_campaign_message_dict["remind_step"] = None
        set_campaign_message_dict["msg_resv_date"] = camp_resv_date
        set_campaign_message_dict["created_by"] = user_id
        set_campaign_message_dict["updated_by"] = user_id

        set_group_messages_all.append(set_campaign_message_dict)

        if remind_dict:
            set_group_remind_messages = []
            for r_idx in range(len(remind_dict)):
                remind_date = remind_dict[r_idx]["remind_date"]
                media = remind_dict[r_idx]["remind_media"]
                msg_type = initial_msg_type[media]

                set_remind_message_dict = {
                    "set_group_seq": set_campaign_message_dict["set_group_seq"],
                    "set_seq": set_campaign_message_dict["set_seq"],
                    "msg_type": msg_type,
                    "media": media,
                    "msg_body": msg_body,
                    "bottom_text": bottom_text,
                    "phone_callback": phone_callback,
                    "campaign_id": campaign_id,
                    "msg_send_type": "remind",
                    "is_used": True,  # 기본값 True
                    "remind_step": remind_dict[r_idx]["remind_step"],
                    "msg_resv_date": remind_date,
                    "created_by": user_id,
                    "updated_by": user_id,
                }

                set_group_remind_messages.append(set_remind_message_dict)

            set_group_messages_all.extend(set_group_remind_messages)

    db.bulk_insert_mappings(SetGroupMessagesEntity, set_group_messages_all)

    return True
