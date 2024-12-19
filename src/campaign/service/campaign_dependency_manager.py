from sqlalchemy import func

from src.audience.infra.entity.audience_entity import AudienceEntity
from src.audience.model.audience_status import AudienceStatus
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.model.campagin_status import CampaignStatus
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.model.strategy_status import StrategyStatus
from src.user.domain.user import User


class CampaignDependencyManager:
    def __init__(self, user: User):
        self.user = user

    def is_object_deletable(self, campaign_obj) -> bool:
        """
        삭제 가능한 캠페인 상태
         - 임시저장(r1)
        """
        if campaign_obj.campaign_status_code == CampaignStatus.tempsave.value:
            return True
        else:
            return False

    def is_object_updatable(self, campaign_obj) -> bool:
        """
        수정 가능한 캠페인 상태
        - 임시저장(r1)
        - 수정단계(r2)
        """
        if campaign_obj.campaign_status_code == CampaignStatus.tempsave.value:
            return True
        elif campaign_obj.campaign_status_code == CampaignStatus.modify.value:
            return True
        else:
            return False

    def sync_campaign_base(self, db, campaign_id, selected_themes, strategy_theme_ids) -> None:
        """
        수정 또는 생성 후
        캠페인 테마 sync
        """
        if selected_themes != strategy_theme_ids:
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).update(
                {"strategy_theme_ids": list(strategy_theme_ids)}
            )

    def sync_strategy_status(self, db, strategy_id) -> None:
        """
        수정 또는 생성 후
        전략 상태 sync
        """

        db.query(StrategyEntity).filter(StrategyEntity.strategy_id == strategy_id).update(
            {
                "strategy_status_code": StrategyStatus.active.value,
                "strategy_status_name": StrategyStatus.active.description,
            }
        )

    def sync_audience_status(self, db, campaign_id, audience_ids=None) -> None:
        """
        수정 또는 생성 후
        오디언스 상태 sync
        """
        new_audience_ids_query = (
            db.query(func.distinct(CampaignSetsEntity.audience_id))
            .filter(CampaignSetsEntity.campaign_id == campaign_id)
            .all()
        )

        new_audience_ids = [aud_id[0] for aud_id in new_audience_ids_query]

        if audience_ids:
            # 삭제된 오디언스 상태 업데이트 -> inactive
            removed_ids = [item for item in audience_ids if item not in new_audience_ids]
            inactive_update = []
            if len(removed_ids) > 0:
                active_audience_query = (
                    db.query(func.distinct(CampaignSetsEntity.audience_id))
                    .join(
                        CampaignEntity,
                        CampaignSetsEntity.campaign_id == CampaignEntity.campaign_id,
                    )
                    .filter(
                        CampaignSetsEntity.campaign_id != campaign_id,
                        CampaignSetsEntity.audience_id.in_(removed_ids),
                        CampaignEntity.campaign_status_code.not_in(
                            ["o2", "s3"]
                        ),  # 활성으로 사용되고 있는 오디언스
                    )
                    .all()
                )

                active_audiences = [aud_id[0] for aud_id in active_audience_query]
                for inactive_aud_id in removed_ids:
                    if inactive_aud_id not in active_audiences:
                        inactive_update.append(inactive_aud_id)

                if len(inactive_update) > 0:
                    db.query(AudienceEntity).filter(
                        AudienceEntity.audience_id.in_(inactive_update)
                    ).update(
                        {
                            "audience_status_code": AudienceStatus.inactive.value,
                            "audience_status_name": AudienceStatus.inactive.description,
                        }
                    )
                    # db.commit()
        else:
            audience_ids = []

        # 추가된 오디언스 상태 업데이트 -> active
        added_ids = [item for item in new_audience_ids if item not in audience_ids]
        if len(added_ids) > 0:
            db.query(AudienceEntity).filter(AudienceEntity.audience_id.in_(added_ids)).update(
                {
                    "audience_status_code": AudienceStatus.active.value,
                    "audience_status_name": AudienceStatus.active.description,
                }
            )
            # db.commit()
