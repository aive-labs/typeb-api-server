from sqlalchemy.orm import Session

from src.audience.routes.port.usecase.update_cycle_usecase import (
    AudienceUpdateCycleUseCase,
)
from src.audience.service.port.base_audience_repository import BaseAudienceRepository
from src.main.transactional import transactional


class AudienceUpdateCycleService(AudienceUpdateCycleUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    @transactional
    def exec(self, audience_id: str, update_cycle: str, db: Session):
        self.audience_repository.update_cycle(audience_id, update_cycle, db)
