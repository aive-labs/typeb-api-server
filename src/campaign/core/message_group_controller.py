from random import choice

from fastapi import HTTPException

from src.campaign.domain.campaign_messages import Message, MessageGenerate
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.message_template.enums.message_type import MessageType


class MessageGroupController:
    def __init__(self, phone_callback, campaign_base, set_group_msg_info) -> None:
        self.campaign_base = campaign_base
        self.set_group_msg_info = set_group_msg_info
        self.vender_bottom_txt = {
            "dau": "무료수신거부 080-801-7860",
            "ssg": "무료수신거부 080-801-7860",
        }
        self.phone_callback = phone_callback  # 매장번호 또는 본사 대표번호

    def pre_define_campaign_msg_seq(self):
        self.campaign_msg_gen_key = [
            item.set_group_message.msg_gen_key
            for item in self.set_group_msg_info
            if item.set_group_message.msg_send_type == "campaign"
            and item.set_group_message.msg_gen_key is not None
        ]
        return self.campaign_msg_gen_key

    def pre_define_remind_msg_seq(self, remind_step):
        self.remind_msg_gen_key = [
            item.set_group_message.msg_gen_key
            for item in self.set_group_msg_info
            if item.set_group_message.msg_send_type == "remind"
            and item.set_group_message.msg_gen_key is not None
            and item.set_group_message.remind_step == remind_step
        ]
        return self.remind_msg_gen_key

    def get_set_group_seq(self, set_group_msg_seq):
        msg_seq_row = [
            item
            for item in self.set_group_msg_info
            if item.set_group_message.set_group_msg_seq == set_group_msg_seq
        ][0]
        return msg_seq_row.set_group_message.set_group_seq

    def get_msg_obj_from_seq(self, set_group_msg_seq):
        msg_seq_row = [
            item
            for item in self.set_group_msg_info
            if item.set_group_message.set_group_msg_seq == set_group_msg_seq
        ][0]

        msg_data = msg_seq_row.set_group_message  # SetGroupMessages
        kakao_btn = [link.__dict__ for link in msg_data.kakao_button_links]

        media = msg_data.media
        msg_type = msg_data.msg_type

        if media is None:
            medias = ["kft", "tms"]
            msg_type_dict = {
                "kft": ["kakao_image_general", "kakao_image_wide"],
                "tms": ["lms"],
            }

            media = choice(medias)
            msg_type = choice(msg_type_dict[media])

        if msg_data.msg_photo_uri:
            msg_type_photo = {
                "kakao_image_general": "kakao_image_general",
                "kakao_image_wide": "kakao_image_wide",
                "kakao_text": "kakao_image_wide",  # 알림텍스트 (방어코드)
                "lms": "mms",
                "sms": "mms",
                "mms": "mms",
            }
            msg_type = msg_type_photo[msg_type]

        msg_obj = MessageGenerate(
            set_group_msg_seq=set_group_msg_seq,
            msg_resv_date=msg_data.msg_resv_date,
            msg_title=msg_data.msg_title if msg_data.msg_title is not None else "",
            msg_body=msg_data.msg_body if msg_data.msg_body is not None else "",
            bottom_text=self.vender_bottom_txt[
                self.campaign_base.msg_delivery_vendor.value
            ],  # 매장 번호 또는 대표번호
            msg_announcement="",
            template_id=None,
            msg_gen_key=(msg_data.msg_gen_key if msg_data.msg_gen_key is not None else None),
            msg_photo_uri=(msg_data.msg_photo_uri if msg_data.msg_photo_uri else None),
            msg_send_type=msg_data.msg_send_type,
            media=media,
            msg_type=msg_type,
            kakao_button_links=kakao_btn,  # [] empty list or [{},{}]list of dict
            phone_callback=self.phone_callback,  # 매장 번호 또는 대표번호
            is_used=msg_data.is_used,
        )
        return msg_obj


def message_image_validator(msg_obj: Message):
    msg_type_dict = {
        "mms": "MMS",
        "kakao_image_general": "카카오 이미지 일반형",
        "kakao_image_wide": "카카오 와이드형",
    }

    if msg_obj.msg_type.value in ("mms", "kakao_image_general", "kakao_image_wide") and (
        msg_obj.msg_photo_uri is None or len(msg_obj.msg_photo_uri) == 0
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message",
                "message": f"{msg_type_dict[msg_obj.msg_type.value]}은(는) 이미지가 포함되어야 합니다.",
            },
        )
    return msg_obj


def message_modify_validator(msg_delivery_vendor: str, msg_obj: Message):
    msg_obj.msg_title = "" if msg_obj.msg_title is None else msg_obj.msg_title

    if msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value:
        encode_type = "UTF-8"  # dau 40byte
    else:
        encode_type = "euc-kr"  # ssg 96byte

    str_to_encode = msg_obj.msg_title
    encode_str = str_to_encode.encode(encode_type)
    encode_size = len(encode_str)

    # 제목 validation checker
    if (msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value) and (encode_size > 40):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message/dau/title_size",
                "message": f"DAU 문자 메세지 제목은 40 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
            },
        )

    if (msg_delivery_vendor == MsgDeliveryVendorEnum.SSG.value) and (encode_size > 96):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message/ssg/title_size",
                "message": f"SSG 문자 메세지 제목은 96 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
            },
        )

    if len(msg_obj.msg_body) > 1000:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message",
                "message": "본문은 1000자 이하로 입력해주세요.",
            },
        )

    # 메시지 타입별 validation checker
    if msg_obj.media.value == "tms":
        if msg_obj.msg_photo_uri:
            msg_obj.msg_type = MessageType.MMS
        elif len(msg_obj.msg_body + msg_obj.bottom_text) < 45:
            msg_obj.msg_type = MessageType.SMS
        else:
            msg_obj.msg_type = MessageType.LMS
    elif msg_obj.media.value == "kft":
        if msg_obj.msg_type.value == "kakao_image_general":
            if len(msg_obj.msg_body) > 400:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 일반형은 400자 이하이어야 합니다.",
                    },
                )
        if msg_obj.msg_type.value == "kakao_text":
            if len(msg_obj.msg_body) > 1000:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 텍스트형은 1000자 이하이어야 합니다.",
                    },
                )
        if msg_obj.msg_type.value == "kakao_image_wide":
            if len(msg_obj.msg_body) > 76:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 와이드형은 76자 이하이어야 합니다.",
                    },
                )

    return msg_obj


def message_validator(msg_delivery_vendor: str, msg_obj: Message):
    msg_obj.msg_title = "" if msg_obj.msg_title is None else msg_obj.msg_title

    if msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value:
        encode_type = "UTF-8"  # dau 40byte
    else:
        encode_type = "euc-kr"  # ssg 96byte

    str_to_encode = msg_obj.msg_title
    encode_str = str_to_encode.encode(encode_type)
    encode_size = len(encode_str)

    # 제목 validation checker
    if (msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value) and (encode_size > 40):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message/dau/title_size",
                "message": f"DAU 문자 메세지 제목은 40 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
            },
        )

    if (msg_delivery_vendor == MsgDeliveryVendorEnum.SSG.value) and (encode_size > 96):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message/ssg/title_size",
                "message": f"SSG 문자 메세지 제목은 96 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
            },
        )

    if len(msg_obj.msg_body) > 1000:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "campaign/message",
                "message": "본문은 1000자 이하로 입력해주세요.",
            },
        )

    # 메시지 타입별 validation checker
    if msg_obj.media.value == "tms":
        if (msg_obj.msg_type == MessageType.MMS.value) & (not msg_obj.msg_photo_uri):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "campaign/message",
                    "message": "MMS는 이미지가 포함되어야 합니다.",
                },
            )

        if (msg_obj.msg_type == MessageType.SMS.value) & (
            len(msg_obj.msg_body + msg_obj.bottom_text) > 45
        ):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "campaign/message",
                    "message": "SMS는 45자 이하이어야 합니다.",
                },
            )

    elif msg_obj.media.value == "kft":
        if msg_obj.msg_type.value == "kakao_image_general":
            if len(msg_obj.msg_body) > 400:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 일반형은 400자 이하이어야 합니다.",
                    },
                )
        if msg_obj.msg_type.value == "kakao_text":
            if len(msg_obj.msg_body) > 1000:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 텍스트형은 1000자 이하이어야 합니다.",
                    },
                )
        if msg_obj.msg_type.value == "kakao_image_wide":
            if len(msg_obj.msg_body) > 76:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 와이드형은 76자 이하이어야 합니다.",
                    },
                )

    return msg_obj
