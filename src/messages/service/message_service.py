import re

import aiohttp
from sqlalchemy.orm import Session

from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import PolicyException, PpurioException
from src.core.transactional import transactional
from src.message_template.enums.message_type import MessageType
from src.messages.infra.ppurio_message_repository import PpurioMessageRepository
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class MessageService:

    def __init__(
        self,
        message_repository: PpurioMessageRepository,
        campaign_repository: BaseCampaignRepository,
    ):
        self.message_repository = message_repository
        self.campaign_repository = campaign_repository
        self.account = get_env_variable("ppurio_account")
        self.file_upload_url = get_env_variable("ppurio_file_upload_url")

    @transactional
    def save_message_result(self, ppurio_message_result: PpurioMessageResult, db: Session):
        self.message_repository.save_message_result(ppurio_message_result, db)

        if self.is_message_success(ppurio_message_result):
            if ppurio_message_result.REFKEY:
                self.campaign_repository.update_send_reservation_status_to_success(
                    ppurio_message_result.REFKEY, db
                )
        else:
            if ppurio_message_result.REFKEY:
                self.campaign_repository.update_send_reservation_status_to_failure(
                    ppurio_message_result.REFKEY, db
                )

    def is_message_success(self, ppurio_message_result):
        if ppurio_message_result.MEDIA == "LMS":
            return ppurio_message_result.MEDIA == "LMS" and ppurio_message_result.RESULT == "6600"
        if ppurio_message_result.MEDIA == "MMS":
            return ppurio_message_result.MEDIA == "MMS" and ppurio_message_result.RESULT == "6600"
        if ppurio_message_result.MEDIA == "SMS":
            return ppurio_message_result.MEDIA == "SMS" and ppurio_message_result.RESULT == "4100"
        if ppurio_message_result.MEDIA in ("KAT", "KFT", "KFP"):
            return (
                ppurio_message_result.MEDIA in ("KAT", "KFT", "KFP")
                and ppurio_message_result.RESULT == "7000"
            )
        # TODO 로그로 전환
        print("지원되지 않는 매체 타입입니다.")
        return False

    async def upload_file(self, new_file_name, file_read, content_type: str | None) -> str:

        # 파일 크기 확인 (300 KB = 300 * 1024 bytes)
        max_size = 300 * 1024
        if len(file_read) > max_size:
            raise PolicyException(detail={"message": "이미지 파일의 크기는 300KB 이하여야 합니다."})

        async with aiohttp.ClientSession() as session:
            url = get_env_variable("ppurio_file_upload_url")
            account = get_env_variable("ppurio_account")

            data = aiohttp.FormData()
            data.add_field("account", account)
            data.add_field(
                "file",
                file_read,
                filename=new_file_name,
                content_type=content_type,
            )

            async with session.post(url, data=data, ssl=False) as response:
                if response.status != 200:
                    print(await response.text())
                    raise PpurioException(
                        detail={
                            "message": "이미지 업로드에 실패하였습니다. 잠시 후에 다시 시도해주세요."
                        }
                    )
                response = await response.json()
        return response["filekey"]

    async def upload_file_for_kakao(
        self, new_file_name: str, file_read, content_type: str | None, message_type: str
    ) -> str:
        if message_type in (MessageType.KAKAO_IMAGE_GENERAL.value, MessageType.KAKAO_TEXT.value):
            # 친구톡 이미지, 텍스트(?)
            image_type = "I"
        else:
            # 친구톡 와이드
            image_type = "W"

        async with aiohttp.ClientSession() as session:
            url = get_env_variable("ppurio_kakao_image_upload_url")

            data = aiohttp.FormData()
            data.add_field("bizId", get_env_variable("ppurio_account"))
            data.add_field("apiKey", get_env_variable("kakao_api_key"))
            data.add_field("imageType", image_type)
            data.add_field("title", new_file_name)
            data.add_field("link", "www.aivelabs.com")
            data.add_field("senderKey", get_env_variable("kakao_sender_key"))

            data.add_field(
                "image",
                file_read,
                filename=new_file_name,
                content_type=content_type,
            )

            async with session.post(url, data=data, ssl=False) as response:
                if response.status != 200:
                    raise PpurioException(
                        detail={
                            "message": "이미지 업로드에 실패하였습니다. 잠시 후에 다시 시도해주세요."
                        }
                    )

                response = await response.json()

                if response["code"] != "0000":
                    match = re.search(r"Exception\((.*?)\)$", response["message"])
                    if match:
                        extracted_message = match.group(1)
                    else:
                        extracted_message = response["message"]

                    raise PolicyException(detail={"message": extracted_message})

        return response["image"]
