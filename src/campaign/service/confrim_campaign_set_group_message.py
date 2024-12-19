from sqlalchemy.orm import Session

from src.campaign.domain.campaign_messages import Message
from src.campaign.routes.port.confirm_campaign_set_group_message_usecase import (
    ConfirmCampaignSetGroupMessageUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.main.exceptions.exceptions import NotFoundException, PolicyException
from src.main.transactional import transactional
from src.message_template.enums.message_type import MessageType


class ConfirmCampaignSetGroupMessage(ConfirmCampaignSetGroupMessageUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def exec(self, campaign_id, set_seq, is_confirmed_obj, user, db: Session):
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)

        if not campaign:
            raise NotFoundException(
                detail={"message": "메시지가 속한 캠페인 정보를 찾지 못했습니다."}
            )

        campaign_set_groups = self.campaign_set_repository.get_campaign_set_group(
            campaign_id, set_seq, db
        )

        msg_delivery_vendor = campaign.msg_delivery_vendor
        for msg_obj in campaign_set_groups:
            if msg_obj.msg_type == MessageType.KAKAO_CAROUSEL.value:
                carousel_cards = self.campaign_set_repository.get_carousel(
                    msg_obj.set_group_msg_seq, db
                )
                if len(carousel_cards) < 2:
                    raise PolicyException(
                        detail={"message": "캐러셀 항목은 2개 이상 입력해야 합니다."}
                    )

            message_model = Message.from_set_group_message(msg_obj)
            self.message_validator(msg_delivery_vendor, message_model)
            self.message_image_validator(message_model)

        self.campaign_set_repository.update_message_confirm_status(
            campaign_id, set_seq, is_confirmed_obj.is_confirmed, db
        )

    def message_image_validator(self, msg_obj: Message):

        msg_type_dict = {
            "mms": "MMS",
            "kakao_image_general": "카카오 이미지 일반형",
            "kakao_image_wide": "카카오 와이드형",
        }

        if msg_obj.msg_type is None:
            raise PolicyException(
                detail={
                    "message": "메시지 타입 값이 없습니다. 확인이 필요합니다.",
                },
            )

        if msg_obj.msg_type.value in ("mms", "kakao_image_general", "kakao_image_wide") and (
            msg_obj.msg_photo_uri is None or len(msg_obj.msg_photo_uri) == 0
        ):
            raise PolicyException(
                detail={
                    "code": "campaign/message",
                    "message": f"{msg_type_dict[msg_obj.msg_type.value]}은(는) 이미지가 포함되어야 합니다.",
                },
            )
        return msg_obj

    def message_validator(self, msg_delivery_vendor: str, msg_obj: Message):
        msg_obj.msg_title = "" if msg_obj.msg_title is None else msg_obj.msg_title
        message_body = msg_obj.msg_body if msg_obj.msg_body else ""
        message_bottom_text = msg_obj.bottom_text if msg_obj.bottom_text else ""

        if msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value:
            encode_type = "UTF-8"  # dau 40byte
        else:
            encode_type = "euc-kr"  # ssg 96byte

        str_to_encode = msg_obj.msg_title
        encode_str = str_to_encode.encode(encode_type)
        encode_size = len(encode_str)

        # 제목 validation checker
        if (msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value) and (encode_size > 40):
            raise PolicyException(
                detail={
                    "code": "campaign/message/dau/title_size",
                    "message": f"DAU 문자 메세지 제목은 40 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
                },
            )

        if (msg_delivery_vendor == MsgDeliveryVendorEnum.SSG.value) and (encode_size > 96):
            raise PolicyException(
                detail={
                    "code": "campaign/message/ssg/title_size",
                    "message": f"SSG 문자 메세지 제목은 96 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
                },
            )

        if len(message_body) > 1000:
            raise PolicyException(
                detail={
                    "code": "campaign/message",
                    "message": "본문은 1000자 이하로 입력해주세요.",
                },
            )

        if msg_obj.media is None:
            raise PolicyException(
                detail={
                    "message": "캠페인 매체 값이 없습니다. 확인이 필요합니다.",
                },
            )

        if msg_obj.msg_type is None:
            raise PolicyException(
                detail={
                    "message": "메시지 타입 값이 없습니다. 확인이 필요합니다.",
                },
            )

        # 메시지 타입별 validation checker
        if msg_obj.media.value == "tms":
            if (msg_obj.msg_type == MessageType.MMS.value) & (msg_obj.msg_photo_uri is None):
                raise PolicyException(
                    detail={
                        "code": "campaign/message",
                        "message": "MMS는 이미지가 포함되어야 합니다.",
                    },
                )

            if (msg_obj.msg_type == MessageType.SMS.value) & (
                len(message_body + message_bottom_text) > 45
            ):
                raise PolicyException(
                    detail={"code": "campaign/message", "message": "SMS는 45자 이하이어야 합니다."},
                )

        elif msg_obj.media.value == "kft":
            if msg_obj.msg_type.value == "kakao_image_general":
                if len(message_body) > 400:
                    raise PolicyException(
                        detail={
                            "code": "campaign/message",
                            "message": "카카오 이미지 일반형은 400자 이하이어야 합니다.",
                        },
                    )
            if msg_obj.msg_type.value == "kakao_text":
                if len(message_body) > 1000:
                    raise PolicyException(
                        detail={
                            "code": "campaign/message",
                            "message": "카카오 텍스트형은 1000자 이하이어야 합니다.",
                        },
                    )
            if msg_obj.msg_type.value == "kakao_image_wide":
                if len(message_body) > 76:
                    raise PolicyException(
                        detail={
                            "code": "campaign/message",
                            "message": "카카오 이미지 와이드형은 76자 이하이어야 합니다.",
                        },
                    )

        return msg_obj
