import aiohttp

from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import PpurioException
from src.message_template.enums.message_type import MessageType
from src.messages.infra.ppurio_message_repository import PpurioMessageRepository
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class MessageService:

    def __init__(self, message_repository: PpurioMessageRepository):
        self.message_repository = message_repository
        self.account = get_env_variable("ppurio_account")
        self.file_upload_url = get_env_variable("ppurio_file_upload_url")

    def save_message_result(self, ppurio_message_result: PpurioMessageResult):
        self.message_repository.save_message_result(ppurio_message_result)

        if self.is_lms_success(ppurio_message_result):
            print("lms success")
            # TODO send_reservation DB 성공 상태 업데이트

    def is_lms_success(self, ppurio_message_result):
        return ppurio_message_result.MEDIA == "LMS" and ppurio_message_result.RESULT == "6600"

    async def upload_file(self, new_file_name, file_read, content_type: str | None) -> str:

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
                    raise PpurioException(
                        detail={"message": "문자 발송 서버에 이미지 업로드 요청이 실패하였습니다."}
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
            data.add_field("link", "https://www.aivelabs.com")
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
                        detail={"message": "문자 발송 서버에 이미지 업로드 요청이 실패하였습니다."}
                    )

                response = await response.json()

                if response["code"] != "200":
                    raise PpurioException(detail={"message": response["message"]})

                print("kakao upload response")
                print(response)
        return response["image"]
