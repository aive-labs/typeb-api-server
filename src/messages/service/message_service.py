import aiohttp
from fastapi import UploadFile

from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import PpurioException
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

    async def upload_file(self, new_file_name, file: UploadFile) -> str:

        async with aiohttp.ClientSession() as session:
            url = "https://api.bizppurio.com/v1/file"

            file_read = await file.read()
            data = aiohttp.FormData()
            data.add_field("account", "aivelabs_dev")
            data.add_field(
                "file",
                file_read,
                filename=new_file_name,
                content_type=file.content_type,
            )

            async with session.post(url, data=data, ssl=False) as response:
                if response.status != 200:
                    raise PpurioException(
                        detail={"message": "문자 발송 서버에 이미지 업로드 요청이 실패하였습니다."}
                    )
                response = await response.json()
        return response["filekey"]
