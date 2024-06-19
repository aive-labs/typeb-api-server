from src.audiences.routes.port.usecase.update_cycle_usecase import (
    AudienceUpdateCycleUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository


class AudienceUpdateCycleService(AudienceUpdateCycleUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def exec(self, audience_id: str, update_cycle: str):
        self.audience_repository.update_cycle(audience_id, update_cycle)
