from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class SendMessageLogEntity(Base):
    __tablename__ = "send_message_logs"

    refkey = Column(String(100), nullable=False, primary_key=True)
    http_status_code = Column(Integer, nullable=False)
    ppurio_messagekey = Column(String(2000), nullable=True)
    http_request_body = Column(String, nullable=True)
    ppurio_status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    send_resv_seq = Column(Integer, nullable=True)
