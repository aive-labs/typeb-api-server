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
            raise NotFoundException(detail={"message": "해당 state은 유효하지 않습니다."})

        return GAIntegration.init(
            mall_id=ga_info.mall_id,
            ga_account_id=ga_info.ga_account_id,
            ga_account_name=ga_info.ga_account_name,
            gtm_account_id=ga_info.gtm_account_id,
            gtm_account_name=ga_info.gtm_account_name,
        )
