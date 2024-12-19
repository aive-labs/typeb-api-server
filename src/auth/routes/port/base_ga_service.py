from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.auth.model.response.ga_script_response import (
    GAScriptResponse,
)
from src.main.transactional import transactional
from src.user.domain.user import User


class BaseGAIntegrationService(ABC):

    @transactional
    @abstractmethod
    async def execute_ga_automation(self, user: User, db: Session) -> GAIntegration:
        pass

    @abstractmethod
    def generate_ga_script(self, user: User, db: Session) -> GAScriptResponse:
        pass

    @transactional
    @abstractmethod
    async def update_status(self, user: User, to_status: str, db: Session):
        pass
