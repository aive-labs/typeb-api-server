from sqlalchemy.orm import Session

from src.campaign.domain.campaign_messages import SetGroupMessage
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity


def get_set_group_msg(campaign_id: str, set_group_msg_seq: int, db: Session) -> SetGroupMessage:
    entity = (
        db.query(SetGroupMessagesEntity)
        .filter(
            SetGroupMessagesEntity.campaign_id == campaign_id,
            SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
        )
        .first()
    )

    return SetGroupMessage.model_validate(entity)


def save_set_group_msg(
    campaign_id: str, set_group_msg_seq: int, message: SetGroupMessage, db: Session
):
    print(message.model_dump())

    saved_entity = SetGroupMessagesEntity(
        set_group_msg_seq=message.set_group_msg_seq,
        set_group_seq=message.set_group_seq,
        msg_send_type=message.msg_send_type,
        remind_step=message.remind_step,
        remind_seq=message.remind_seq,
        msg_resv_date=message.msg_resv_date,
        set_seq=message.set_seq,
        campaign_id=message.campaign_id,
        media=message.media,
        msg_type=message.msg_type,
        msg_title=message.msg_title,
        msg_body=message.msg_body,
        msg_gen_key=message.msg_gen_key,
        rec_explanation=message.rec_explanation,
        bottom_text=message.bottom_text,
        msg_announcement=message.msg_announcement,
        template_id=message.template_id,
        msg_photo_uri=message.msg_photo_uri,
        phone_callback=message.phone_callback,
        is_used=message.is_used,
        created_at=message.created_at,
        created_by=message.created_by,
        updated_at=message.updated_at,
        updated_by=message.updated_by,
    )

    if message.kakao_button_links:
        print("save_button_links")
        kakao_button_link_list = [
            KakaoLinkButtonsEntity(
                kakao_link_buttons_seq=kakao_button.kakao_link_buttons_seq,
                set_group_msg_seq=kakao_button.set_group_msg_seq,
                button_name=kakao_button.button_name,
                button_type=kakao_button.button_type,
                web_link=kakao_button.web_link,
                app_link=kakao_button.app_link,
                created_at=kakao_button.created_at,
                created_by=kakao_button.created_by,
                updated_at=kakao_button.updated_at,
                updated_by=kakao_button.updated_by,
            )
            for kakao_button in message.kakao_button_links
        ]

        saved_entity.kakao_button_links = kakao_button_link_list

    if message.msg_resources:
        message_source_list = [
            MessageResourceEntity(
                resource_id=message_source.resource_id,
                set_group_msg_seq=message_source.set_group_msg_seq,
                resource_name=message_source.resource_name,
                resource_path=message_source.resource_path,
                img_uri=message_source.img_uri,
                link_url=message_source.link_url,
                landing_url=message_source.landing_url,
            )
            for message_source in message.msg_resources
        ]

        saved_entity.msg_resources = message_source_list

    db.merge(saved_entity)
