from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity


def delete_excluded_campaign_sets(db: Session, campaign_id: str, set_seqs: list):
    # 삭제할 set_group_seqs 추출
    delete_to_seqs = (
        db.query(CampaignSetsEntity.set_seq, CampaignSetsEntity.set_sort_num)
        .filter(
            CampaignSetsEntity.campaign_id == campaign_id, ~CampaignSetsEntity.set_seq.in_(set_seqs)
        )
        .all()
    )

    set_sort_nums = []
    # CampaignSetGroups 오브젝트 삭제 -연결된 오브젝트 삭제 SetGroupMessages, ...
    for d_seq in delete_to_seqs:
        deleted_obj = (
            db.query(CampaignSetsEntity)
            .filter(
                CampaignSetsEntity.campaign_id == campaign_id,
                CampaignSetsEntity.set_seq == d_seq[0],
            )
            .first()
        )
        db.delete(deleted_obj)
        set_sort_nums.append(d_seq[1])

    # recipient 삭제 필요여부 확인
    delete_statement = delete(CampaignSetRecipientsEntity).where(
        CampaignSetRecipientsEntity.campaign_id == campaign_id,
        CampaignSetRecipientsEntity.set_sort_num.in_(
            set_sort_nums
        ),  # pyright: ignore [reportCallIssue]
    )

    db.execute(delete_statement)

    return True
