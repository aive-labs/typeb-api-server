import time

import aioboto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException, UploadFile
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository
from src.campaign.domain.campaign_messages import Message
from src.campaign.domain.vo.carousel_upload_link import CarouselUploadLinks
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
    NotFoundException,
    PolicyException,
)
from src.message_template.enums.message_type import MessageType
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.service.message_service import MessageService
from src.users.domain.user import User


class UploadImageForMessage(UploadImageForMessageUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        message_service: MessageService,
        onboarding_repository: BaseOnboardingRepository,
        s3_service: S3Service,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.message_service = message_service
        self.onboarding_repository = onboarding_repository
        self.s3_service = s3_service
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

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
            s3_file_key = f"{user.mall_id}/messages_resource/{campaign_id}/{set_group_msg_seq}/images/{new_file_name}"

            try:
                file_read = await file.read()

                # 뿌리오 MMS 이미지 업로드
                ppurio_filekey = None
                if message_type in (
                    MessageType.MMS.value,
                    MessageType.LMS.value,
                    MessageType.SMS.value,
                ):
                    ppurio_filekey = await self.message_service.upload_file(
                        new_file_name, file_read, file.content_type
                    )

                # 카카오 이미지 업로드
                kakao_sender_key = self.onboarding_repository.get_kakao_sender_key(
                    mall_id=user.mall_id, db=db
                )
                if kakao_sender_key is None:
                    raise NotFoundException(
                        detail={"messsage": "등록된 kakao sender key가 존재하지 않습니다."}
                    )

                kakao_landing_url = await self.message_service.upload_file_for_kakao(
                    new_file_name, file_read, file.content_type, message_type, kakao_sender_key
                )

                # s3에 이미지 저장
                await self.s3_service.put_object_async(s3_file_key, file_read)

            except Exception as e:
                await self.s3_service.delete_object_async(s3_file_key)
                if isinstance(e, HTTPException):
                    raise e
                else:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "이미지 업로드에 실패하였습니다. 잠시 후 다시 시도해주세요."
                        },
                    ) from e
            finally:
                await file.close()

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
                "img_uri": f"{self.cloud_front_url}/{message_entity.img_uri}",
                "link_url": message_entity.link_url,
            }
            message_resources.append(selected_data)

        # set_group_messages에 img_uri 저장
        # 누적 등록 기능 없음
        if message_photo_uri:
            self.campaign_set_repository.update_message_image(
                campaign_id, set_group_msg_seq, message_photo_uri, db
            )

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

    async def upload_for_carousel(
        self, file: UploadFile, carousel_card: KakaoCarouselCard, user: User, db: Session
    ) -> CarouselUploadLinks:

        # 파일 이름 변경(unix timestamp)
        set_group_msg_seq = carousel_card.set_group_msg_seq
        campaign_id = self.campaign_set_repository.get_campaign_by_set_group_message_by_msg_seq(
            set_group_msg_seq, db
        )
        new_file_name = self.generate_timestamp_file_name(file.filename)
        s3_file_key = f"{user.mall_id}/messages_resource/{campaign_id}/{set_group_msg_seq}/images/{new_file_name}"

        try:
            file_read = await file.read()

            # 카카오 이미지 업로드
            kakao_sender_key = self.onboarding_repository.get_kakao_sender_key(
                mall_id=user.mall_id, db=db
            )
            if kakao_sender_key is None:
                raise NotFoundException(
                    detail={"messsage": "등록된 kakao sender key가 존재하지 않습니다."}
                )

            kakao_landing_url = await self.message_service.upload_file_for_kakao_carousel(
                new_file_name,
                file_read,
                file.content_type,
                kakao_sender_key,
                carousel_card.image_title,
                carousel_card.image_link,
            )

            # s3에 이미지 저장
            await self.s3_service.put_object_async(s3_file_key, file_read)

            return CarouselUploadLinks(
                kakao_image_link=kakao_landing_url, s3_image_path=s3_file_key
            )

        except Exception as e:
            await self.s3_service.delete_object_async(s3_file_key)
            if isinstance(e, HTTPException):
                raise e
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "message": "이미지 업로드에 실패하였습니다. 잠시 후 다시 시도해주세요."
                    },
                ) from e
        finally:
            await file.close()
