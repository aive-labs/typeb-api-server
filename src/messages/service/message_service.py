import re

import aiohttp
from sqlalchemy.orm import Session

from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import PolicyException, PpurioException
from src.core.transactional import transactional
from src.message_template.enums.message_type import MessageType
from src.messages.infra.message_repository import MessageRepository
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class MessageService:

    def __init__(
        self,
        message_repository: MessageRepository,
        campaign_repository: BaseCampaignRepository,
    ):
        self.message_repository = message_repository
        self.campaign_repository = campaign_repository
        self.account = get_env_variable("ppurio_account")
        self.file_upload_url = get_env_variable("ppurio_file_upload_url")

    @transactional
    def save_message_result(self, ppurio_message_result: PpurioMessageResult, db: Session):

        if ppurio_message_result.REFKEY is None:
            raise PolicyException(detail={"message": "refkey가 존재하지 않습니다."})

        send_resv_seq = ppurio_message_result.REFKEY.split("==")[1]

        ppurio_message_result.send_resv_seq = send_resv_seq
        self.message_repository.save_message_result(ppurio_message_result, db)

        if self.is_message_success(ppurio_message_result):
            self.campaign_repository.update_send_reservation_status_to_success(send_resv_seq, db)
        else:
            self.campaign_repository.update_send_reservation_status_to_failure(send_resv_seq, db)

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
        self,
        new_file_name: str,
        file_read,
        content_type: str | None,
        message_type: str,
        kakao_sender_key: str,
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
            data.add_field("link", "www.aivelabs.com")  # TODO 쇼핑몰 링크 넣도록 수정
            data.add_field("senderKey", kakao_sender_key)

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

                if response["code"] not in ["200", "0000"]:
                    print("code", response["code"])
                    print(response)
                    match = re.search(r"Exception\((.*?)\)$", response["message"])
                    if match:
                        extracted_message = match.group(1)
                    else:
                        extracted_message = response["message"]

                    raise PolicyException(detail={"message": extracted_message})

        return response["image"]

    async def upload_file_for_kakao_carousel(
        self, new_file_name, file_read, content_type, kakao_sender_key, image_title, image_link
    ) -> str:

        max_size = 2 * 1024 * 1024
        print(f"max_size: {max_size}")
        if len(file_read) > max_size:
            raise PolicyException(detail={"message": "이미지 파일의 크기는 2MB 이하여야 합니다."})

        async with aiohttp.ClientSession() as session:
            print(1)
            url = get_env_variable("ppurio_kakao_carousel_image_upload_url")

            data = aiohttp.FormData()
            data.add_field("bizId", get_env_variable("ppurio_account"))
            data.add_field("apiKey", get_env_variable("kakao_api_key"))
            data.add_field("senderKey", kakao_sender_key)

            print(2)
            data.add_field(
                "imageList[0].image", file_read, filename=new_file_name, content_type=content_type
            )
            data.add_field("imageList[0].title", image_title)
            data.add_field("imageList[0].link", image_link)  # 링크를 실제 값으로 대체하세요

            print(3)
            async with session.post(url, data=data, ssl=False) as response:
                print(response.status)
                upload_response = await response.json()
                print(upload_response)
                if response.status != 200:
                    raise PpurioException(
                        detail={
                            "message": "이미지 업로드에 실패하였습니다. 잠시 후에 다시 시도해주세요."
                        }
                    )

                response = upload_response

                if response["code"] not in ["200", "0000"]:
                    print("code", response["code"])
                    print(response)

                    error_message = "이미지 업로드에 실패하였습니다. 잠시 후에 다시 시도해주세요."
                    if response["code"] == "6000":
                        match = re.search(
                            r"Exception\((.*?)\)$",
                            response["data"]["failure"][0]["error"]["message"],
                        )
                        if match:
                            error_message = match.group(1)
                    if response["code"] == "405":
                        error_message = response["message"]

                    raise PolicyException(detail={"message": error_message})

        return response["data"]["success"][0]["url"]
