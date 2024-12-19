from sqlalchemy.orm import Session

from src.common.enums.access_level import AccessLevel
from src.main.exceptions.exceptions import AuthorizationException
from src.main.transactional import transactional
from src.message_template.domain.message_template import MessageTemplate
from src.message_template.domain.message_template_button_detail import (
    MessageTemplateButtonDetail,
)
from src.message_template.infra.message_template_repository import (
    MessageTemplateRepository,
)
from src.message_template.routes.dto.request.message_template_update import (
    TemplateUpdate,
)
from src.message_template.routes.port.update_message_template_usecase import (
    UpdateMessageTemplateUseCase,
)
from src.user.domain.user import User


class UpdateMessageTemplateService(UpdateMessageTemplateUseCase):

    def __init__(self, message_template_repository: MessageTemplateRepository):
        self.message_template_repository = message_template_repository

    @transactional
    def exec(self, template_id: str, template_update: TemplateUpdate, user: User, db: Session):

        template_update.template_id = int(template_id)
        # if admin -> 1
        access_level = [level.value for level in AccessLevel if level.name == user.role_id][0]

        old_template = self.message_template_repository.get_template_detail(template_id, db)

        if old_template.access_level < access_level:
            raise AuthorizationException(
                detail={"message": "해당 템플릿에 대한 수정 권한이 없습니다."}
            )

        # 한번 생성한 템플릿은 부서를 변경할 수 없음
        update_message_template: MessageTemplate = MessageTemplate(
            template_id=template_update.template_id,
            template_name=template_update.template_name,
            media=template_update.media.value,
            message_title=template_update.message_title,
            message_body=template_update.message_body,
            message_announcement=template_update.message_announcement,
            template_key=template_update.template_key,
            access_level=template_update.access_level,
            owned_by_dept=user.department_id if user.department_id else "",
            owned_by_dept_name=user.department_name if user.department_name else "",
            updated_by=user.username,
        )
        # 메시지 타입 정의
        update_message_template.set_message_type()

        if template_update.button:
            for _, data in enumerate(template_update.button):
                button_item = MessageTemplateButtonDetail(
                    button_id=data.button_id,
                    template_id=data.template_id,
                    button_name=data.button_name,
                    button_type=data.button_type.value,
                    web_link=data.web_link,
                    app_link=data.app_link,
                )
                update_message_template.button.append(button_item)

        self.message_template_repository.update(template_id, update_message_template, db)
