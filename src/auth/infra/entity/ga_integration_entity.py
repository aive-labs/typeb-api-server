from sqlalchemy import BigInteger, Column, DateTime, String, func

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
