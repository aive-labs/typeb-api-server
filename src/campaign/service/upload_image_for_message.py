import time

import aioboto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.campaign.domain.campaign_messages import Message
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.routes.port.upload_image_for_message_usecase import (
    UploadImageForMessageUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.utils.file.s3_service import S3Service
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import (
    ConsistencyException,
    PolicyException,
)
from src.core.transactional import transactional
from src.message_template.enums.message_type import MessageType
from src.messages.service.message_service import MessageService


class UploadImageForMessage(UploadImageForMessageUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        message_service: MessageService,
        s3_service: S3Service,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.message_service = message_service
        self.s3_service = s3_service

    @transactional
    async def exec(
        self, campaign_id, set_group_msg_seq, files: list[UploadFile], user, db: Session
    ) -> dict:
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db=db)
        self.check_already_delivered_message(campaign, campaign_id, db, set_group_msg_seq)

        set_group_message = self.campaign_set_repository.get_campaign_set_group_message_by_msg_seq(
            campaign_id, set_group_msg_seq, db
        )
        message_type = set_group_message.msg_type

        if message_type is None:
            raise ConsistencyException(detail={"message": "메시지 타입이 존재하지 않습니다."})

        original_message_photo_uri = set_group_message.msg_photo_uri

        message_photo_uri = []
        message_resources = []
        for file in files:
            # 파일 이름 변경(unix timestamp)
            new_file_name = self.generate_timestamp_file_name(file.filename)

            # s3에 이미지 저장
            s3_file_key = f"{user.mall_id}/messages_resource/{campaign_id}/{set_group_msg_seq}/images/{new_file_name}"
            await self.s3_service.put_object_async(s3_file_key, file)
            print("s3_file_key")
            print(s3_file_key)

            # 뿌리오 MMS 이미지 업로드
            ppurio_filekey = None
            if message_type == MessageType.MMS.value:
                ppurio_filekey = await self.message_service.upload_file(new_file_name, file)
            print("ppurio_filekey")
            print(ppurio_filekey)

            # 카카오 이미지 업로드
            kakao_landing_url = None
            if self.is_message_type_kakao(message_type):
                kakao_landing_url = await self.message_service.upload_file_for_kakao(
                    new_file_name, file, message_type
                )
            print("kakao_landing_url")
            print(kakao_landing_url)

            # 기존 이미지 삭제
            if original_message_photo_uri is not None and len(original_message_photo_uri) > 0:
                delete_statement = delete(MessageResourceEntity).where(
                    MessageResourceEntity.set_group_msg_seq == set_group_msg_seq
                )
                db.execute(delete_statement)

            # db에 new_image_resource 추가
            message_entity = MessageResourceEntity(
                set_group_msg_seq=set_group_msg_seq,
                resource_name=s3_file_key,
                resource_path=s3_file_key,
                img_uri=s3_file_key,
                link_url=ppurio_filekey,
                landing_url=kakao_landing_url,
            )
            message_photo_uri.append(s3_file_key)

            db.add(message_entity)
            db.flush()

            selected_data = {
                "resource_id": message_entity.resource_id,
                "img_uri": message_entity.img_uri,
                "link_url": message_entity.link_url,
            }
            message_resources.append(selected_data)

        # set_group_messages에 img_uri 저장  msg_photo_uri: List[]
        group_msg_dict = jsonable_encoder(set_group_message)
        for key, value in group_msg_dict.items():
            if key == "msg_photo_uri":
                value = message_photo_uri  # 누적 등록 기능 없음
                setattr(set_group_message, key, value)

        # 메세지 타입 업데이트(ex) sms-> mms)
        new_message_type = self.adjust_message_type_on_image_upload(message_type)
        self.update_message_type(
            campaign_id, db, new_message_type, set_group_message, set_group_msg_seq
        )

        # 이미지 등록 후 메세지 검증
        set_group_message = self.campaign_set_repository.get_campaign_set_group_message_by_msg_seq(
            campaign_id, set_group_msg_seq, db
        )
        message = Message.from_set_group_message(set_group_message)

        db.commit()

        return {
            "set_group_msg_seq": set_group_msg_seq,
            "msg_obj": message,
            "resources": message_resources,
        }

    def is_message_type_kakao(self, message_type):
        return message_type in (
            MessageType.KAKAO_TEXT.value,
            MessageType.KAKAO_IMAGE_GENERAL.value,
            MessageType.KAKAO_IMAGE_WIDE.value,
        )

    def update_message_type(
        self, campaign_id, db, new_message_type, set_group_message, set_group_msg_seq
    ):
        if set_group_message.msg_send_type == "campaign":
            db.query(CampaignSetGroupsEntity).filter(
                CampaignSetGroupsEntity.campaign_id == campaign_id,
                CampaignSetGroupsEntity.set_group_seq == set_group_message.set_group_seq,
            ).update({CampaignSetGroupsEntity.msg_type: new_message_type})
        db.query(SetGroupMessagesEntity).filter(
            SetGroupMessagesEntity.campaign_id == campaign_id,
            SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
        ).update({SetGroupMessagesEntity.msg_type: new_message_type})
        db.flush()

    def adjust_message_type_on_image_upload(self, message_type):
        if message_type in (
            MessageType.SMS.value,
            MessageType.LMS.value,
            MessageType.MMS.value,
        ):
            update_msg_type = MessageType.MMS.value

        elif message_type in (
            MessageType.KAKAO_TEXT.value,
            MessageType.KAKAO_IMAGE_GENERAL.value,
        ):
            update_msg_type = MessageType.KAKAO_IMAGE_GENERAL.value
        elif message_type == MessageType.KAKAO_IMAGE_WIDE.value:
            update_msg_type = MessageType.KAKAO_IMAGE_WIDE.value
        else:
            raise ConsistencyException(detail={"message": "Invalid msg type"})
        return update_msg_type

    def check_already_delivered_message(self, campaign, campaign_id, db, set_group_msg_seq):
        if campaign.campaign_status_code == "r2":
            # 발송된 메세지 수정 불가
            send_msg_first = (
                db.query(SendReservationEntity)
                .filter(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.set_group_msg_seq == set_group_msg_seq,
                    SendReservationEntity.send_resv_state.not_in(
                        ["21", "01", "00"]
                    ),  # 발송한 메세지 필터
                )
                .first()
            )
            if send_msg_first:
                raise PolicyException(
                    detail={
                        "code": "message/update/denied",
                        "message": "이미 발송된 메세지는 수정이 불가합니다.",
                    },
                )

    def generate_timestamp_file_name(self, filename):
        ext = filename.split(".")[-1]
        # Unix 타임스탬프로 파일명 생성
        timestamp = int(time.time())
        timestamp_filename = f"{timestamp}.{ext}"
        return timestamp_filename

    async def upload_to_s3(self, file: UploadFile, filename: str):

        s3_bucket = get_env_variable("s3_asset_bucket")

        session = aioboto3.Session()
        async with session.client("s3") as s3:
            try:
                file_content = await file.read()
                await s3.put_object(Bucket=s3_bucket, Key=filename, Body=file_content)
                return {"status": "success", "message": "file uploaded to s3"}
            except NoCredentialsError:
                return {"status": "error", "message": "credentials not available"}
