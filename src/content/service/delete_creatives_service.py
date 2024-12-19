from sqlalchemy.orm import Session

from src.content.enums.image_source import ImageSource
from src.content.infra.creatives_repository import CreativesRepository
from src.content.routes.port.usecase.delete_creatives_usecase import (
    DeleteCreativesUseCase,
)
from src.core.exceptions.exceptions import PolicyException
from src.core.transactional import transactional


class DeleteCreativesService(DeleteCreativesUseCase):

    def __init__(self, creatives_repository: CreativesRepository):
        self.creatives_repository = creatives_repository

    @transactional
    def exec(self, creative_id: int, db: Session) -> None:
        creative = self.creatives_repository.get_creatives_by_id(creative_id, db)
        if creative.image_source == ImageSource.CAFE24.value:
            raise PolicyException(
                detail={"message": "cafe24에서 업로드한 이미지는 삭제할 수 없습니다."}
            )

        self.creatives_repository.delete(creative_id, db)
