from sqlalchemy import func
from sqlalchemy.orm import Session

from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity


def get_message_resources(db: Session, set_group_msg_seqs: list):
    link_url_query = (
        db.query(
            MessageResourceEntity.set_group_msg_seq.label("set_group_msg_seq"),
            func.array_agg(MessageResourceEntity.link_url).label("send_filepath"),
            func.cardinality(func.array_agg(MessageResourceEntity.link_url)).label(
                "send_filecount"
            ),
        )
        .filter(
            MessageResourceEntity.set_group_msg_seq.in_(
                set_group_msg_seqs
            ),  # link_url이 NULL이 아닌 행만 선택
            MessageResourceEntity.link_url != None,  # link_url이 NULL이 아닌 행만 선택
        )
        .group_by(MessageResourceEntity.set_group_msg_seq)  # set_group_msg_seq 별로 그룹화
    )

    landing_url_query = (
        db.query(
            MessageResourceEntity.set_group_msg_seq.label("set_group_msg_seq"),
            func.array_agg(MessageResourceEntity.landing_url).label("send_filepath"),
            func.cardinality(func.array_agg(MessageResourceEntity.landing_url)).label(
                "send_filecount"
            ),
        )
        .filter(
            MessageResourceEntity.set_group_msg_seq.in_(
                set_group_msg_seqs
            ),  # link_url이 NULL이 아닌 행만 선택
            MessageResourceEntity.landing_url != None,  # link_url이 NULL이 아닌 행만 선택
        )
        .group_by(MessageResourceEntity.set_group_msg_seq)  # set_group_msg_seq 별로 그룹화
    )

    union_query = link_url_query.union(landing_url_query)

    return union_query
