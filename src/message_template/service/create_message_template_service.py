from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.common.enums.campaign_media import CampaignMedia
from src.main.exceptions.exceptions import ValidationException
from src.main.transactional import transactional
from src.message_template.domain.message_template import MessageTemplate
from src.message_template.domain.message_template_button_detail import (
    MessageTemplateButtonDetail,
)
from src.message_template.enums.message_type import MessageType
from src.message_template.routes.dto.request.message_template_create import (
    TemplateCreate,
)
from src.message_template.routes.port.create_message_template_usecase import (
    CreateMessageTemplateUseCase,
)
from src.message_template.service.port.base_message_template_repository import (
    BaseMessageTemplateRepository,
)
from src.user.domain.user import User


class CreateMessageTemplateService(CreateMessageTemplateUseCase):

    def __init__(self, message_template_repository: BaseMessageTemplateRepository):
        self.message_template_repository = message_template_repository

    @transactional
    def exec(self, template_create: TemplateCreate, user: User, db: Session) -> MessageTemplate:

        selected_media = template_create.media
        message_title = template_create.message_title
        message_body = template_create.message_body
        message_announcement = (
            template_create.message_announcement if template_create.message_announcement else ""
        )

        if selected_media == CampaignMedia.KAKAO_ALIM_TALK:
            message_type = MessageType.KAKAO_ALIM_TEXT
            if len(message_title) > 31:
                raise ValidationException(detail="템플릿키의 길이는 30자를 초과할 수 없습니다.")
            if len(message_body + message_announcement) > 1000:
                raise ValidationException(
                    detail="메시지 본문과 안내문구의 총 길이는 1000자를 초과할 수 없습니다."
                )
        elif selected_media == CampaignMedia.TEXT_MESSAGE:
            if len(message_body) <= 80:
                message_type = MessageType.SMS
            elif len(message_body) <= 1000:
                message_type = MessageType.LMS
            else:
                raise ValidationException(detail="메시지 본문은 1000자를 초과할 수 없습니다.")
        else:
            raise ValidationException(detail="템플릿은 카카오 알림톡과 LMS(SMS)만 가능합니다.")

        message_template = MessageTemplate(
            template_name=template_create.template_name,
            media=template_create.media.value,
            message_type=message_type.value,  # enum to value
            message_title=template_create.message_title,
            message_body=template_create.message_body,
            message_announcement=template_create.message_announcement,
            template_key=template_create.template_key,
            access_level=template_create.access_level,
            owned_by_dept=user.department_id if user.department_id else "",
            owned_by_dept_name=user.department_name if user.department_name else "",
            created_by=str(user.user_id),
            created_at=datetime.now(timezone.utc),
            updated_by=str(user.user_id),
            updated_at=datetime.now(timezone.utc),
        )

        if template_create.button:
            for _, data in enumerate(template_create.button):
                button_item = MessageTemplateButtonDetail(
                    button_name=data.button_name,
                    button_type=data.button_type.value,
                    web_link=data.web_link,
                    app_link=data.app_link,
                )
                message_template.button.append(button_item)

        return self.message_template_repository.save_message_template(message_template, db)
