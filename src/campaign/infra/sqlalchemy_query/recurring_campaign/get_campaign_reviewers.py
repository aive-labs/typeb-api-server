from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.infra.dto.campaign_reviewer_info import CampaignReviewerInfo
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import CampaignApprovalEntity
from src.user.infra.entity.user_entity import UserEntity


def get_campaign_reviewers(campaign_id: str, db: Session) -> list[CampaignReviewerInfo]:
    entities = (
        db.query(
            CampaignApprovalEntity.approval_no,
            ApproverEntity.user_id,
            ApproverEntity.user_name,
            ApproverEntity.is_approved,
            ApproverEntity.department_abb_name,
            UserEntity.test_callback_number,
            ApproverEntity.is_approved,
        )
        .join(ApproverEntity, CampaignApprovalEntity.approval_no == ApproverEntity.approval_no)
        .outerjoin(UserEntity, ApproverEntity.user_id == UserEntity.user_id)
        .filter(
            and_(
                CampaignApprovalEntity.campaign_id == campaign_id,
                or_(
                    CampaignApprovalEntity.approval_status
                    == CampaignApprovalStatus.REVIEW.value,  # 수정요청 받은 결재의 승인자
                    CampaignApprovalEntity.approval_status
                    == CampaignApprovalStatus.APPROVED.value,  # 승인된 결재의 승인자
                ),
            )
        )
        .all()
    )

    return [CampaignReviewerInfo.model_validate(entity) for entity in entities]
