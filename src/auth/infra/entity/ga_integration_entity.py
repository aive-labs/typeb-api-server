from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, String, func

from src.auth.domain.ga_integration import GAIntegration
from src.core.database import Base


class GAIntegrationEntity(Base):
    __tablename__ = "ga_integration"

    mall_id = Column(String, primary_key=True, nullable=False)
    ga_account_id = Column(BigInteger, nullable=False)
    ga_account_name = Column(String, nullable=False)
    ga_property_id = Column(BigInteger, nullable=True)
    ga_property_name = Column(String, nullable=True)
    ga_measurement_id = Column(String, nullable=True)
    ga_data_stream_id = Column(BigInteger, nullable=True)
    ga_data_stream_uri = Column(String, nullable=True)
    ga_data_stream_name = Column(String, nullable=True)
    ga_data_stream_type = Column(String, nullable=True)
    gtm_account_id = Column(BigInteger, nullable=False)
    gtm_account_name = Column(String, nullable=False)
    gtm_container_id = Column(BigInteger, nullable=True)
    gtm_container_name = Column(String, nullable=True)
    gtm_tag_id = Column(String, nullable=True)
    ga_script = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    @staticmethod
    def from_model(model: GAIntegration):
        return GAIntegrationEntity(
            mall_id=model.mall_id,
            ga_account_id=model.ga_account_id,
            ga_account_name=model.ga_account_name,
            ga_property_id=model.ga_property_id,
            ga_property_name=model.ga_property_name,
            ga_measurement_id=model.ga_measurement_id,
            ga_data_stream_id=model.ga_data_stream_id,
            ga_data_stream_uri=model.ga_data_stream_uri,
            ga_data_stream_name=model.ga_data_stream_name,
            ga_data_stream_type=model.ga_data_stream_type,
            gtm_account_id=model.gtm_account_id,
            gtm_account_name=model.gtm_account_name,
            gtm_container_id=model.gtm_container_id,
            gtm_container_name=model.gtm_container_name,
            gtm_tag_id=model.gtm_tag_id,
            ga_script=model.ga_script,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
