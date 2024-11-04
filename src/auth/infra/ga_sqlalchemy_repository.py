from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.auth.infra.entity.ga_integration_entity import GAIntegrationEntity
from src.core.exceptions.exceptions import NotFoundException


class GASqlAlchemyRepository:

    def get_by_mall_id(self, mall_id, db: Session) -> GAIntegration:
        ga_info = (
            db.query(GAIntegrationEntity).filter(GAIntegrationEntity.mall_id == mall_id).first()
        )

        if not ga_info:
            raise NotFoundException(
                detail={"message": "구글 애널리틱스 연동 데이터가 존재하지 않습니다."}
            )

        return GAIntegration(
            mall_id=ga_info.mall_id,
            ga_account_id=ga_info.ga_account_id,
            ga_account_name=ga_info.ga_account_name,
            gtm_account_id=ga_info.gtm_account_id,
            gtm_account_name=ga_info.gtm_account_name,
            ga_measurement_id=ga_info.ga_measurement_id,
            gtm_tag_id=ga_info.gtm_tag_id,
        )

    def save_ga_integration(self, ga_integration: GAIntegration, db: Session):
        entity = GAIntegrationEntity.from_model(ga_integration)
        db.merge(entity)
