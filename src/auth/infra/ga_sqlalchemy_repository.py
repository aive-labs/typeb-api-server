from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.auth.enums.ga_script_status import GAScriptStatus
from src.auth.infra.entity.ga_integration_entity import GAIntegrationEntity
from src.common.utils.get_env_variable import get_env_variable


class GASqlAlchemyRepository:

    def get_by_mall_id(self, mall_id, db: Session) -> GAIntegration:
        ga_info = (
            db.query(GAIntegrationEntity).filter(GAIntegrationEntity.mall_id == mall_id).first()
        )

        if not ga_info:
            entity = GAIntegrationEntity(
                mall_id=mall_id,
                ga_account_id=int(get_env_variable("aace_ga_account_id")),
                ga_account_name=get_env_variable("aace_ga_account_name"),
                gtm_account_id=int(get_env_variable("aace_gtm_account_id")),
                gtm_account_name=get_env_variable("aace_gtm_account_name"),
                ga_script_status="pending",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(entity)
            db.commit()

            ga_info = (
                db.query(GAIntegrationEntity).filter(GAIntegrationEntity.mall_id == mall_id).first()
            )

        return GAIntegration(
            mall_id=ga_info.mall_id,
            ga_account_id=ga_info.ga_account_id,
            ga_account_name=ga_info.ga_account_name,
            gtm_account_id=ga_info.gtm_account_id,
            gtm_account_name=ga_info.gtm_account_name,
            ga_measurement_id=ga_info.ga_measurement_id,
            gtm_tag_id=ga_info.gtm_tag_id,
            ga_script_status=GAScriptStatus(ga_info.ga_script_status),
        )

    def save_ga_integration(self, ga_integration: GAIntegration, db: Session):
        entity = GAIntegrationEntity.from_model(ga_integration)
        db.merge(entity)

    def update_status(self, mall_id, to_status, db):
        db.query(GAIntegrationEntity).filter(GAIntegrationEntity.mall_id == mall_id).update(
            {"ga_script_status": to_status}
        )
