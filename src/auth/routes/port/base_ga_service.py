from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.core.transactional import transactional
from src.users.domain.user import User


class BaseGAIntegrationService(ABC):

    @transactional
    @abstractmethod
    async def execute_ga_automation(self, mall_id: str, user: User, db: Session) -> GAIntegration:
        pass
