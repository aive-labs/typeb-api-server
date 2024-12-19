from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.model.request.test_send_request import TestSendRequest
from src.user.domain.user import User


class TestSendMessageUseCase(ABC):

    @abstractmethod
    async def exec(
        self, campaign_id, test_send_request: TestSendRequest, user: User, db: Session
    ) -> dict:
        pass
