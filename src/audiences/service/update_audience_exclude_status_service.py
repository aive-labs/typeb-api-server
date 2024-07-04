from src.audiences.routes.port.usecase.update_audience_exclude_status import (
    UpdateAudienceExcludeStatusUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository


class UpdateAudienceExcludeStatusService(UpdateAudienceExcludeStatusUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def exec(self, audience_id, is_exclude, user):
        self.audience_repository.update_exclude_status(audience_id, is_exclude)
