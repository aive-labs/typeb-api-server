from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, func

from src.core.database import Base
from src.payment.domain.cafe24_payment import Cafe24Payment
from src.users.domain.user import User


class Cafe24PaymentEntity(Base):
    __tablename__ = "cafe24_payments"

    order_id = Column(String, primary_key=True, nullable=False)  # PK로 설정
    payment_status = Column(String, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    approval_no = Column(String, nullable=False)
    payment_gateway_name = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_amount = Column(Float, nullable=False)
    refund_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    locale_code = Column(String, nullable=False)
    automatic_payment = Column(String, nullable=False)
    pay_date = Column(DateTime, nullable=False)
    refund_date = Column(DateTime, nullable=True)  # Optional 필드
    expiration_date = Column(DateTime, nullable=False)

    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())

    @staticmethod
    def from_model(cafe24_payment: Cafe24Payment, user: User):
        return Cafe24PaymentEntity(
            order_id=cafe24_payment.order_id,
            payment_status=cafe24_payment.payment_status.value,
            title=cafe24_payment.title,
            approval_no=cafe24_payment.approval_no,
            payment_gateway_name=cafe24_payment.payment_gateway_name,
            payment_method=cafe24_payment.payment_method,
            payment_amount=cafe24_payment.payment_amount,
            refund_amount=cafe24_payment.refund_amount,
            currency=cafe24_payment.currency,
            locale_code=cafe24_payment.locale_code,
            automatic_payment=cafe24_payment.automatic_payment,
            pay_date=cafe24_payment.pay_date,
            refund_date=cafe24_payment.refund_date,
            expiration_date=cafe24_payment.expiration_date,
            created_by=user.user_id,
            created_at=datetime.now(timezone.utc),
            updated_by=user.user_id,
            updated_at=datetime.now(timezone.utc),
        )
