from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class PaymentEntity(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_key = Column(String, primary_key=True)
    order_id = Column(String, nullable=False)
    order_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    requested_at = Column(String, nullable=False)
    approved_at = Column(String, nullable=True)
    type = Column(String, nullable=False)

    card_number = Column(String, nullable=True)
    card_type = Column(String, nullable=True)
    card_company = Column(String, nullable=True)

    receipt_url = Column(String, nullable=True)
    checkout_url = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    total_amount = Column(Integer, nullable=False)
    balance_amount = Column(Integer, nullable=False)
    supplied_amount = Column(Integer, nullable=False)
    vat = Column(Integer, nullable=False)
    tax_free_amount = Column(Integer, nullable=False)
    method = Column(String, nullable=False)
    version = Column(String, nullable=False)

    product_type = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
