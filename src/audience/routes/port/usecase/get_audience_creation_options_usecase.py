from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audience.model.response.upload_condition_response import (
    AudienceCreationOptionsResponse,
)


class GetAudienceCreationOptionsUseCase(ABC):

    @abstractmethod
    def get_filter_conditions(
        self, audience_id: str, db: Session
    ) -> AudienceCreationOptionsResponse:
        pass

    @abstractmethod
    def get_csv_uploaded_data(
        self, audience_id: str, db: Session
    ) -> AudienceCreationOptionsResponse:
        pass
