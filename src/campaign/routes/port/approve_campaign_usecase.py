from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.domain.user import User


class ApproveCampaignUseCase(ABC):

    @abstractmethod
    async def exec(
        self,
        campaign_id,
        to_status,
        db: Session,
        user: User,
        reviewers: str | None = None,
    ) -> dict:
        pass

    @abstractmethod
    def save_campaign_reservation(self, db, user_obj, campaign_id, msg_seqs_to_save=None):
        pass

    @abstractmethod
    def save_campaign_logs(
        self,
        db,
        campaign_id,
        timeline_type,
        created_at,
        created_by,
        created_by_name,
        to_status=None,
        status_no=None,
        description=None,
        approval_excute=False,
    ) -> bool:
        pass
