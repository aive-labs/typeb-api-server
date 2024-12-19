from sqlalchemy import Column, DateTime, String, func

from src.main.database import Base as Base


class SendDagLogEntity(Base):
    __tablename__ = "send_dag_log"

    campaign_id = Column(String(20), nullable=False)
    send_resv_date = Column(DateTime(timezone=True), nullable=False)
    dag_run_id = Column(String, nullable=False, primary_key=True)
    etl_time = Column(DateTime(timezone=True), default=func.now())
