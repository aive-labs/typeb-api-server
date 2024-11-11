from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)

from src.core.database import Base


class SendMessageLogs(Base):
    __tablename__ = "send_message_logs"
    __table_args__ = (
        PrimaryKeyConstraint("refkey", "http_status_code", name="send_message_logs_pkey"),
        {"schema": "aivelabs_sv"},
    )

    refkey = Column(String(100), nullable=False)
    http_status_code = Column(Integer, nullable=False)
    ppurio_messagekey = Column(String(2000), nullable=True)
    http_request_body = Column(Text, nullable=True)
    ppurio_status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    send_resv_seq = Column(Integer, nullable=True)
