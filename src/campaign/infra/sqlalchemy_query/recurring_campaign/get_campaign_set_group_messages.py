from sqlalchemy import inspect
from sqlalchemy.orm import Session, subqueryload

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.common.utils.get_env_variable import get_env_variable


def get_campaign_set_group_messages(campaign_id: str, db: Session) -> list:
    query_result = (
        db.query(
            SetGroupMessagesEntity,
            CampaignSetGroupsEntity.set_seq,
            CampaignSetGroupsEntity.group_sort_num,
        )
        .outerjoin(CampaignSetGroupsEntity)
        .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
        .options(subqueryload(SetGroupMessagesEntity.kakao_button_links))
        .all()
    )

    result_list = []
    for item in query_result:
        set_group_message, set_seq, group_sort_num = item

        # SetGroupMessages 객체를 딕셔너리로 변환
        set_group_message_dict = {
            c.key: getattr(set_group_message, c.key)
            for c in inspect(set_group_message).mapper.column_attrs
        }

        # 메시지 경로 변경
        if set_group_message.msg_photo_uri:
            cloud_front_url = get_env_variable("cloud_front_asset_url")
            set_group_message_dict["msg_photo_uri"] = [
                f"{cloud_front_url}/{uri}" for uri in set_group_message.msg_photo_uri
            ]

        # 관련된 kakao_button_links를 딕셔너리 리스트로 변환
        set_group_message_dict["kakao_button_links"] = [
            {c.key: getattr(link, c.key) for c in inspect(link).mapper.column_attrs}
            for link in set_group_message.kakao_button_links
        ]

        # CampaignSetGroups의 컬럼을 딕셔너리에 추가
        set_group_message_dict["set_seq"] = set_seq
        set_group_message_dict["group_sort_num"] = group_sort_num

        result_list.append(set_group_message_dict)

    return result_list
