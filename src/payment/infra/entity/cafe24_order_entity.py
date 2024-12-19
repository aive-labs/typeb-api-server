from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, func

from src.main.database import Base
from src.payment.domain.cafe24_order import Cafe24Order
from src.user.domain.user import User


class Cafe24OrderEntity(Base):
    __tablename__ = "cafe24_orders"  # 테이블 이름

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)  # 기본키
    order_id = Column(String(64), unique=True, nullable=False)
    cafe24_order_id = Column(String(255), nullable=False)
    order_name = Column(String(255), nullable=False)
    order_amount = Column(Float, nullable=False)
    currency = Column(String(20), nullable=False)
    return_url = Column(String, nullable=False)
    automatic_payment = Column(String(4), nullable=False)
    confirmation_url = Column(String, nullable=False)

    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())

    @staticmethod
    def from_model(cafe24_order: Cafe24Order, user: User):
        return Cafe24OrderEntity(
            order_id=cafe24_order.order_id,
            cafe24_order_id=cafe24_order.cafe24_order_id,
            order_name=cafe24_order.order_name,
            order_amount=cafe24_order.order_amount,
            currency=cafe24_order.currency,
            return_url=cafe24_order.return_url,
            automatic_payment=cafe24_order.automatic_payment,
            confirmation_url=cafe24_order.confirmation_url,
            created_by=user.user_id,
            created_at=datetime.now(timezone.utc),
            updated_by=user.user_id,
            updated_at=datetime.now(timezone.utc),
        )
